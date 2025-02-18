from typing import Optional, List
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from models.invoice import Invoice
from .base import StorageProvider

class CosmosDBProvider(StorageProvider):
    """Implementación del proveedor de almacenamiento usando Azure CosmosDB"""
    
    def __init__(self, connection_string: str, database_name: str = "invoices_db"):
        self.client = CosmosClient.from_connection_string(connection_string)
        self.database_name = database_name
        self.container_name = "invoices"
        self._container = None
    
    async def _get_container(self):
        """Obtiene o crea el contenedor de facturas"""
        if self._container is None:
            database = await self.client.create_database_if_not_exists(self.database_name)
            self._container = await database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/vendor_name"),
                offer_throughput=400
            )
        return self._container
    
    async def save_invoice(self, invoice: Invoice) -> str:
        """
        Guarda una factura en CosmosDB.
        
        Args:
            invoice: Objeto Invoice a guardar
            
        Returns:
            str: ID de la factura guardada
        """
        container = await self._get_container()
        
        # Convertir la factura a diccionario y agregar id
        invoice_dict = invoice.model_dump()
        invoice_dict["id"] = invoice.invoice_number
        
        # Guardar en CosmosDB
        result = await container.create_item(invoice_dict)
        return result["id"]
    
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Recupera una factura por su ID.
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            Optional[Invoice]: La factura si existe
        """
        container = await self._get_container()
        
        try:
            result = await container.read_item(
                item=invoice_id,
                partition_key=invoice_id
            )
            return Invoice(**result)
        except Exception:
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
        container = await self._get_container()
        
        # Construir la consulta SQL
        query = "SELECT * FROM c WHERE 1=1"
        parameters = []
        
        if vendor_name:
            query += " AND c.vendor_name = @vendor_name"
            parameters.append({"name": "@vendor_name", "value": vendor_name})
            
        if date_from:
            query += " AND c.date >= @date_from"
            parameters.append({"name": "@date_from", "value": date_from})
            
        if date_to:
            query += " AND c.date <= @date_to"
            parameters.append({"name": "@date_to", "value": date_to})
        
        # Ejecutar la consulta
        results = []
        async for item in container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ):
            results.append(Invoice(**item))
            
        return results
    
    async def delete_invoice(self, invoice_id: str) -> bool:
        """
        Elimina una factura por su ID.
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            bool: True si se eliminó correctamente
        """
        container = await self._get_container()
        
        try:
            await container.delete_item(
                item=invoice_id,
                partition_key=invoice_id
            )
            return True
        except Exception:
            return False
            
    async def close(self):
        """Cierra la conexión con CosmosDB"""
        if self.client:
            await self.client.close()
