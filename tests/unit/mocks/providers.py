from typing import Dict, Any, Optional, List
from datetime import datetime

from providers.vision.base import VisionProvider
from providers.storage.base import StorageProvider
from models.invoice import Invoice


class MockVisionProvider(VisionProvider):
    """Proveedor de visión simulado para pruebas."""
    
    async def process_image(self, image_data: bytes, model_name: str, api_key: str, **kwargs: Dict[str, Any]) -> dict:
        """Simula el procesamiento de una imagen."""
        return {
            "extracted_text": "FACTURA\nNúmero: INV-001\nFecha: 17/02/2024\nVendedor: Test Company\nNIT: 123456789\n\nItem 1 - 100.00 x 1 = 100.00\n\nSubtotal: 100.00\nIVA: 19.00\nTotal: 119.00 USD",
            "provider": "mock_provider",
            "model": model_name
        }
    
    async def validate_api_key(self, api_key: str) -> bool:
        """Simula la validación de una clave API."""
        return api_key == "test-key" or api_key.startswith("valid-")


class MockStorageProvider(StorageProvider):
    """Proveedor de almacenamiento simulado para pruebas."""
    
    def __init__(self):
        self.invoices = {}
        self.next_id = "INV-001"
    
    async def save_invoice(self, invoice: Invoice) -> str:
        """Simula el guardado de una factura."""
        invoice_id = self.next_id
        self.invoices[invoice_id] = invoice
        self.next_id = f"INV-{int(self.next_id.split('-')[1]) + 1:03d}"
        return invoice_id
    
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Simula la recuperación de una factura."""
        return self.invoices.get(invoice_id)
    
    async def list_invoices(
        self,
        vendor_name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Invoice]:
        """Simula el listado de facturas con filtros."""
        result = list(self.invoices.values())
        
        if vendor_name:
            result = [inv for inv in result if vendor_name.lower() in inv.vendor_name.lower()]
        
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from)
            result = [inv for inv in result if inv.date >= date_from_obj]
        
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to)
            result = [inv for inv in result if inv.date <= date_to_obj]
        
        return result
    
    async def delete_invoice(self, invoice_id: str) -> bool:
        """Simula la eliminación de una factura."""
        if invoice_id in self.invoices:
            del self.invoices[invoice_id]
            return True
        return False
