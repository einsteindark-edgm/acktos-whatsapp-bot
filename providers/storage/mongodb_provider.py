from typing import Optional, List
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import pymongo
from models.invoice import Invoice
from .base import StorageProvider

class MongoDBProvider(StorageProvider):
    """Implementación del proveedor de almacenamiento usando MongoDB"""
    
    def __init__(self, connection_string: str, database_name: str = "invoices_db"):
        self.client = MongoClient(connection_string)
        self.database_name = database_name
        self.collection_name = "invoices"
        self._db = self.client[database_name]
        self._collection = self._db[self.collection_name]
        
        # Crear índices para mejorar las consultas
        self._collection.create_index("invoice_number", unique=True)
        self._collection.create_index("vendor_name")
        self._collection.create_index("date")
    
    async def save_invoice(self, invoice: Invoice) -> str:
        """
        Guarda una factura en MongoDB.
        
        Args:
            invoice: Objeto Invoice a guardar
            
        Returns:
            str: ID de la factura guardada
        """
        # Convertir la factura a diccionario
        invoice_dict = invoice.model_dump()
        invoice_dict["_id"] = invoice.invoice_number
        
        # Guardar en MongoDB
        try:
            self._collection.insert_one(invoice_dict)
            return invoice.invoice_number
        except pymongo.errors.DuplicateKeyError:
            # Si ya existe, actualizar
            self._collection.replace_one({"_id": invoice.invoice_number}, invoice_dict)
            return invoice.invoice_number
    
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Recupera una factura por su ID.
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            Optional[Invoice]: La factura si existe
        """
        result = self._collection.find_one({"_id": invoice_id})
        if result:
            # Eliminar el _id para convertir a Invoice
            result.pop("_id", None)
            return Invoice(**result)
        return None
    
    async def list_invoices(
        self,
        vendor_name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Invoice]:
        """
        Lista facturas con filtros opcionales.
        
        Args:
            vendor_name: Filtrar por vendedor
            date_from: Fecha inicial
            date_to: Fecha final
            
        Returns:
            List[Invoice]: Lista de facturas
        """
        # Construir la consulta
        query = {}
        
        if vendor_name:
            query["vendor_name"] = vendor_name
            
        if date_from or date_to:
            query["date"] = {}
            if date_from:
                query["date"]["$gte"] = date_from
            if date_to:
                query["date"]["$lte"] = date_to
        
        # Ejecutar la consulta
        results = []
        for doc in self._collection.find(query):
            # Eliminar el _id para convertir a Invoice
            doc.pop("_id", None)
            results.append(Invoice(**doc))
            
        return results
    
    async def delete_invoice(self, invoice_id: str) -> bool:
        """
        Elimina una factura por su ID.
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            bool: True si se eliminó correctamente
        """
        result = self._collection.delete_one({"_id": invoice_id})
        return result.deleted_count > 0
            
    async def close(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
