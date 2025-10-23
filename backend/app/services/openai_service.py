import base64
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from app.models.invoice_schema import InvoiceData

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
Du extrahierst strukturierte Daten aus Restaurant-Lieferantenrechnungen (PDF oder Bild). Gib ausschließlich gültiges JSON zurück – ohne Text, Erklärungen oder Formatierung.

Verwende dieses Schema:
{
  "supplier_name": string oder null,
  "supplier_address": string oder null,
  "supplier_vat_id": string oder null,
  "invoice_number": string oder null,
  "invoice_date": "TT-MM-JJJJ" oder null,
  "due_date": "TT-MM-JJJJ" oder null,
  "items": [
    {
      "description": string,
      "quantity": number,
      "unit_price": number,
      "unit": string oder null,
      "net_amount": number,
      "tax_rate": number oder null,
      "tax_amount": number oder null,
      "currency": "EUR",
      "category": string
    }
  ],
  "net_total": number oder null,
  "tax_total": number oder null,
  "gross_total": number oder null,
  "currency": "EUR",
  "payment_method": string oder null,
  "iban": string oder null,
  "notes": string oder null
}

Regeln:

* Nur JSON zurückgeben – kein Text davor oder danach.
* Dezimalzahlen mit Punkt (z. B. 12.50), kein Komma.
* Fehlende, unlesbare oder mehrdeutige Werte = null.
* Nur Informationen verwenden, die auf der Rechnung stehen. Keine Annahmen oder erfundenen Inhalte.
* currency immer "EUR".

Lieferant (supplier):

* Der Lieferant ist immer das Unternehmen, das die Rechnung ausstellt – nicht der Empfänger.
* Erkennbar durch:
  • Firmenname in Kopf- oder Fußzeile neben Rechnungsnummer oder Logo.
  • Bankverbindung, USt-ID oder Zahlungsbedingungen gehören zum Lieferanten.
* Empfänger (z. B. Tigre GmbH) niemals als supplier_name verwenden.

supplier_vat_id:

* Nur ausfüllen, wenn auf der Rechnung klar eine USt-ID (z. B. „DE123456789“) steht.
* Deutsche USt-ID muss exakt dem Format „DE“ + 9 Ziffern entsprechen.
* Steuer-Nr. oder BN ist keine USt-ID.
* Wenn Ziffern fehlen, hinzugefügt wurden oder nicht exakt im Dokument stehen → supplier_vat_id = null.

iban:

* IBAN nur übernehmen, wenn vollständig, exakt und eindeutig auf der Rechnung steht.
* Keine Ziffern ergänzen oder verändern.
* Kein automatisch generiertes oder teilweise korrigiertes Konto.
* Leerzeichen dürfen entfernt werden, aber sonst unverändert belassen.

invoice_date:

* Datum der Rechnung („Rechnungsdatum“, „Belegdatum“).

due_date:

* Wenn ein konkretes Datum genannt wird (z. B. „Zahlbar bis zum 10.05.2025 ohne Abzug“) → exakt übernehmen, nicht berechnen.
* Wenn nur Frist („zahlbar innerhalb 8 Tagen“) → due_date = invoice_date + Anzahl Tage.
* Wenn mehrere Angaben vorkommen (z. B. 8 Tage & 14 Tage):
  1. Text näher an Summen-/Zahlbereich hat Vorrang.
  2. „ohne Abzug“, „netto Kasse“ oder konkreter SEPA-Fälligkeitstermin hat Vorrang.
  3. Wenn weiter unklar → kürzere Frist verwenden.
* Wenn kein eindeutiges Zahlungsziel → due_date = null.
* Widersprüchliche Zahlungsbedingungen dürfen nicht gleichzeitig in notes erscheinen.

items:

* Jede Artikelzeile mit Beschreibung wird als Item erfasst.
* Beschreibung, Menge, Einheit, Preis und Nettobetrag müssen aus der Rechnung stammen.
* tax_rate nur aus tatsächlicher Angabe (z. B. „MwSt 19 %“, „01 = 7 %“).
* tax_amount = net_amount * tax_rate / 100, auf 2 Nachkommastellen runden, außer wenn der exakte Betrag auf der Rechnung steht.

Pfand / Leergut:

* Wenn Pfand (Leergut, Kisten, Flaschen, Fässer) in der Artikelliste mit Preis aufgeführt ist → als Item erfassen.
* category für solche Posten = "Packaging".
* Negative Pfandbeträge (z. B. Rückgabe) auch als Packaging-Item.
* Wenn „Pfand Summe“ separat außerhalb der Artikelliste steht → nicht als Item erfassen.
* Keine separate „deposit“-Struktur verwenden.

category:
* Pflichtfeld bei jedem Item mit Beschreibung.
* Zulässige Werte: Seafood, Meat, Produce, Dairy, Beverages, Service, Cleaning Supplies, Packaging, Other.

Steuer:

* 7 % (oder ST01) = 7.0
* 19 % (oder ST02) = 19.0
* tax_rate = null, wenn kein Wert erkennbar.
* tax_amount exakt berechnen, falls nicht auf der Rechnung ausgewiesen.

notes:

* Nur echten Originaltext wie:
  • Eigentumsvorbehalt,
  • SEPA-Lastschrift Hinweis,
  • Zahlungsform „ohne Abzug“, „netto Kasse“.
* Keine automatisch generierten Texte wie „Bitte überweisen...“, außer es steht exakt so auf der Rechnung.
* Kein erneutes Nennen der IBAN in notes, wenn es nicht wortwörtlich im Dokument steht.
* Keine widersprüchlichen Zahlungsbedingungen kombinieren.

Keine zusätzlichen Felder im JSON.
"""


# --- Clean possible ```json fenced outputs ---
def clean_json_output(raw: str) -> str:
    if not raw:
        return raw
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "").strip()
    return raw


# --- Date normalization into YYYY-MM-DD ---
def normalize_date(date_str: str) -> str | None:
    if not date_str:
        return None

    formats = ["%d.%m.%y", "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except:
            pass
    return date_str  # if model already outputs YYYY-MM-DD, keep it


# --- Normalize data to fit InvoiceData schema & prevent errors ---
def normalize_invoice_schema(data: dict) -> dict:
    # 1. Normalize taxes: can be float or dict
    if isinstance(data.get("tax_total"), (int, float)) and not data.get("taxes"):
        data["tax_total"] = float(data["tax_total"])

    # 2. Discounts: ensure a list of dicts like [{'discount': float}]
    discounts = data.get("discounts")
    if discounts is None:
        data["discounts"] = []
    elif isinstance(discounts, (int, float)):
        data["discounts"] = [{"discount": float(discounts)}]
    elif isinstance(discounts, list):
        fixed = []
        for d in discounts:
            if isinstance(d, (int, float)):
                fixed.append({"discount": float(d)})
            elif isinstance(d, dict):
                for v in d.values():
                    if isinstance(v, (int, float)):
                        fixed.append({"discount": float(v)})
                        break
        data["discounts"] = fixed

    # 3. Normalize invoice_date & due_date
    if data.get("invoice_date"):
        data["invoice_date"] = normalize_date(data["invoice_date"])
    if data.get("due_date"):
        data["due_date"] = normalize_date(data["due_date"])

    # 4. Normalize items (must match InvoiceItem schema)
    items = data.get("items", [])
    if not isinstance(items, list):
        items = []

    cleaned_items = []
    for it in items:
        cleaned_items.append({
            "description": it.get("description", "Unknown"),
            "quantity": float(it.get("quantity") or 1),
            "unit_price": float(it.get("unit_price") or 0),
            "unit": it.get("unit"),
            "net_amount": float(it.get("net_amount") or (float(it.get("quantity") or 1) * float(it.get("unit_price") or 0))),
            "tax_rate": float(it.get("tax_rate")) if it.get("tax_rate") not in (None, "") else None,
            "tax_amount": float(it.get("tax_amount")) if it.get("tax_amount") not in (None, "") else None,
            "currency": it.get("currency") or "EUR",
            "category": it.get("category")  # Preserve category from LLM
        })

    data["items"] = cleaned_items

    return data


# --- Call GPT model ---
def call_model(model_name: str, encoded_image: str, mime_type: str):
    return client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extrahiere JSON aus dieser Rechnung:"},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_image}"}}
                ]
            }
        ],
        max_completion_tokens=4000,
        temperature=0
    )


# --- Main extraction function ---
def extract_invoice_data(image_bytes: bytes, content_type: str = "image/jpeg") -> InvoiceData:
    # Ensure content type is supported by OpenAI
    supported_types = ["image/png", "image/jpeg", "image/gif", "image/webp"]
    if content_type not in supported_types:
        # Default to jpeg if unknown
        content_type = "image/jpeg"

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    # Use GPT-4.1
    response = call_model("gpt-4.1", encoded, content_type)
    raw_output = response.choices[0].message.content

    cleaned = clean_json_output(raw_output or "")

    try:
        data = json.loads(cleaned)
        data = normalize_invoice_schema(data)
        return InvoiceData(**data)
    except Exception as e:
        raise ValueError(
            f"Failed to parse/validate JSON: {e}\nRaw output:\n{raw_output}")
