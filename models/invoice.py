from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class InvoiceItem(BaseModel):
    """Representa un ítem individual en una factura"""
    description: str = Field(description="Descripción del producto o servicio")
    quantity: float = Field(description="Cantidad del producto o servicio", gt=0)
    unit_price: float = Field(description="Precio unitario", gt=0)
    total: float = Field(description="Total para este ítem")

class Invoice(BaseModel):
    """Representa una factura completa"""
    invoice_number: str = Field(description="Número único de la factura")
    date: datetime = Field(description="Fecha de la factura")
    vendor_name: str = Field(description="Nombre del vendedor o empresa")
    vendor_tax_id: Optional[str] = Field(None, description="Identificación fiscal del vendedor")
    total_amount: float = Field(description="Monto total de la factura", gt=0)
    tax_amount: Optional[float] = Field(0.0, description="Monto de impuestos")
    items: List[InvoiceItem] = Field(description="Lista de ítems en la factura")
    currency: str = Field(description="Moneda de la factura", default="USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-001",
                "date": "2024-02-17T00:00:00",
                "vendor_name": "Tech Solutions Inc",
                "vendor_tax_id": "123456789",
                "total_amount": 1150.00,
                "tax_amount": 150.00,
                "items": [
                    {
                        "description": "Laptop Dell XPS 13",
                        "quantity": 1,
                        "unit_price": 1000.00,
                        "total": 1000.00
                    }
                ],
                "currency": "USD"
            }
        }
