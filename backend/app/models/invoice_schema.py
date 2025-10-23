from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class InvoiceItem(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Product A",
                "quantity": 2.0,
                "unit_price": 10.50,
                "unit": "Kg",
                "net_amount": 21.00,
                "tax_rate": 19.0,
                "tax_amount": 3.99,
                "currency": "EUR",
                "category": "Seafood"
            }
        }
    )

    description: str  # required
    quantity: float = 1
    unit_price: float = 0
    unit: Optional[str] = None
    net_amount: float = 0
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    currency: str = "EUR"
    category: Optional[str] = None  # e.g., 'Seafood', 'Beverages', etc.


class InvoiceData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "supplier_name": "Example GmbH",
                "supplier_address": "Example Street 123",
                "invoice_number": "INV-001",
                "invoice_date": "15-01-2025",
                "items": []
            }
        }
    )

    supplier_name: Optional[str] = None
    supplier_address: Optional[str] = None
    supplier_vat_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = Field(
        default=None, pattern=r"^\d{2}-\d{2}-\d{4}$"
    )
    due_date: Optional[str] = Field(
        default=None, pattern=r"^\d{2}-\d{2}-\d{4}$"
    )
    items: List[InvoiceItem] = Field(default_factory=list)
    net_total: Optional[float] = None
    tax_total: Optional[float] = None
    gross_total: Optional[float] = None
    currency: str = "EUR"
    payment_method: Optional[str] = None
    iban: Optional[str] = None
    notes: Optional[str] = None
