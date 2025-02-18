from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from models.dependencies import StorageAgentDependencies
from models.invoice import Invoice

class StorageResult(BaseModel):
    """Resultado de la operación de almacenamiento"""
    invoice_id: str = Field(description="ID de la factura almacenada")
    success: bool = Field(description="Indica si la operación fue exitosa")
    message: str = Field(description="Mensaje descriptivo del resultado")

storage_agent = Agent(
    'openai:gpt-4',
    deps_type=StorageAgentDependencies,
    result_type=StorageResult,
    system_prompt=(
        "Eres un agente especializado en el almacenamiento seguro de facturas. "
        "Tu objetivo es garantizar que cada factura se guarde correctamente y "
        "validar la integridad de los datos antes del almacenamiento."
    )
)

@storage_agent.tool
async def store_invoice(
    ctx: RunContext[StorageAgentDependencies],
    invoice: Invoice
) -> StorageResult:
    """
    Almacena una factura en la base de datos.
    
    Args:
        ctx: Contexto de ejecución
        invoice: Factura a almacenar
        
    Returns:
        StorageResult: Resultado de la operación
    """
    try:
        # Intentar guardar la factura
        invoice_id = await ctx.deps.storage_provider.save_invoice(invoice)
        
        return StorageResult(
            invoice_id=invoice_id,
            success=True,
            message=f"Factura {invoice_id} almacenada correctamente"
        )
    except Exception as e:
        return StorageResult(
            invoice_id="",
            success=False,
            message=f"Error al almacenar la factura: {str(e)}"
        )

@storage_agent.tool
async def verify_storage(
    ctx: RunContext[StorageAgentDependencies],
    invoice_id: str
) -> bool:
    """
    Verifica que una factura se haya almacenado correctamente.
    
    Args:
        ctx: Contexto de ejecución
        invoice_id: ID de la factura a verificar
        
    Returns:
        bool: True si la factura existe y es accesible
    """
    stored_invoice = await ctx.deps.storage_provider.get_invoice(invoice_id)
    return stored_invoice is not None
