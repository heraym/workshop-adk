from google.adk.agents.llm_agent import Agent

def info_producto(producto: str) -> str:
    """Provee informacion y precio de un producto particular.

    Args:
        producto: El codigo de producto.

    Returns:
        La descripcion del producto y el precio.
    """
    if "producto1" in producto.lower() or "1" in producto.lower():
        return { "producto": { "descripcion": "Este es el producto 1", "precio": 100} }
    if "producto2" in producto.lower() or "2" in producto.lower():
        return { "producto": { "descripcion": "Este es el producto 2", "precio": 500} }
    if "producto3" in producto.lower() or "3" in producto.lower():
        return { "producto": { "descripcion": "Este es el producto 3", "precio": 10} }
    return 0

info_agent = Agent(
    model='gemini-2.5-flash',
    name='info_agent',
    description='Un agente que provee informacion de los productos.',
    instruction='Debes proveer informacion de los productos por los que te consultan. Para eso debes usar la tool "info_producto"',
    tools=[info_producto]
)