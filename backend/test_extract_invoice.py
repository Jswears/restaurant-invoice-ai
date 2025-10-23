import requests
import json
import os

url = "http://127.0.0.1:8000/invoices/extract"
file_path = "./invoices_for_test/26.5-El-cielo.pdf"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "application/pdf")}
    print("📤 Sending PDF to API...")
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("✅ Success:")
    result = response.json()

    # Print pretty JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Create output filename based on input filename
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"./structured_invoices/{base_name}-output.json"

    # Save to file with proper JSON formatting
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to {output_file}")
else:
    print(f"❌ Error {response.status_code}: {response.text}")
