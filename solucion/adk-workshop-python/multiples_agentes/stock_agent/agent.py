from google.adk.agents.llm_agent import Agent

def validar_stock(producto: str) -> str:
    """Valida el stock de un producto particular.

    Args:
        producto: El codigo de producto.

    Returns:
        La cantidad de stock que hay de ese producto.
    """
    if "producto1" in producto.lower() or "1" in producto.lower():
        return 50
    if "producto2" in producto.lower() or "2" in producto.lower():
        return 10
    if "producto3" in producto.lower() or "3" in producto.lower():
        return 200
    return 0

stock_agent = Agent(
    model='gemini-2.5-flash',
    name='stock_agent',
    description='Un agente que valida el stock de los productos.',
    instruction='Debes validar que los productos por los que te consultan tienen stock. Para eso debes usar la tool "validar_stock"',
    tools=[validar_stock]
)
