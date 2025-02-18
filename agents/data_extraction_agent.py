from pydantic_ai import Agent, RunContext
from models.dependencies import ExtractorAgentDependencies
from models.invoice import Invoice, InvoiceItem

extraction_agent = Agent(
    'openai:gpt-4',
    deps_type=ExtractorAgentDependencies,
    result_type=Invoice,
    system_prompt=(
        "Eres un agente especializado en extraer información estructurada de texto de facturas. "
        "Tu objetivo es analizar el texto proporcionado y convertirlo en un objeto Invoice válido. "
        "Debes ser preciso en la extracción de números, fechas y montos. "
        "Si algún dato requerido no está presente, debes indicarlo claramente."
    )
)

@extraction_agent.tool
async def parse_invoice_text(
    ctx: RunContext[ExtractorAgentDependencies],
    text: str
) -> Invoice:
    """
    Analiza el texto de una factura y extrae la información en formato estructurado.
    
    Args:
        ctx: Contexto de ejecución
        text: Texto extraído de la factura
        
    Returns:
        Invoice: Objeto Invoice con la información estructurada
    """
    # Este método podría usar otro LLM para estructurar los datos,
    # pero por ahora dejamos que el agente principal lo maneje
    pass

@extraction_agent.tool
async def validate_amounts(
    ctx: RunContext[ExtractorAgentDependencies],
    items: list[InvoiceItem],
    total_amount: float,
    tax_amount: float
) -> bool:
    """
    Valida que los montos de los items coincidan con el total.
    
    Args:
        ctx: Contexto de ejecución
        items: Lista de items de la factura
        total_amount: Monto total declarado
        tax_amount: Monto de impuestos
        
    Returns:
        bool: True si los montos son consistentes
    """
    subtotal = sum(item.total for item in items)
    calculated_total = subtotal + tax_amount
    
    # Permitimos una pequeña diferencia por redondeo
    return abs(calculated_total - total_amount) < 0.01
