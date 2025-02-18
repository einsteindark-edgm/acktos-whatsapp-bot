from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from models.invoice import Invoice

class StorageProvider(ABC):
    """Interfaz base para proveedores de almacenamiento"""
    
    @abstractmethod
    async def save_invoice(self, invoice: Invoice) -> str:
        """
        Guarda una factura en el almacenamiento.
        
        Args:
            invoice: Objeto Invoice a guardar
            
        Returns:
            str: Identificador único de la factura guardada
        """
        pass
    
    @abstractmethod
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Recupera una factura por su ID.
        
        Args:
            invoice_id: ID de la factura a recuperar
            
        Returns:
            Optional[Invoice]: La factura si existe, None si no se encuentra
        """
        pass
    
    @abstractmethod
    async def list_invoices(
        self,
        vendor_name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Invoice]:
        """
        Lista facturas con filtros opcionales.
        
        Args:
            vendor_name: Filtrar por nombre de vendedor
            date_from: Fecha inicial (formato ISO)
            date_to: Fecha final (formato ISO)
            
        Returns:
            List[Invoice]: Lista de facturas que cumplen con los filtros
        """
        pass
    
    @abstractmethod
    async def delete_invoice(self, invoice_id: str) -> bool:
        """
        Elimina una factura por su ID.
        
        Args:
            invoice_id: ID de la factura a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        pass
