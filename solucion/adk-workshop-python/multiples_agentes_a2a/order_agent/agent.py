from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
import random

def order_producto(producto: str, cantidad: int) -> str:
    """Provee informacion y precio de un producto particular.

    Args:
        producto: El codigo de producto.
        cantidad: La cantidad del producto a ordenar.

    Returns:
        El numero de orden
    """
    if "producto1" in producto.lower() or "1" in producto.lower():
        if cantidad > 0:
           return random.randint(1, 10)  
    if "producto2" in producto.lower() or "2" in producto.lower():
        if cantidad > 0:
           return random.randint(1, 10)  
    if "producto3" in producto.lower() or "3" in producto.lower():
        if cantidad > 0:
           return random.randint(1, 10)  
    return 0

order_agent = Agent(
    model='gemini-2.5-flash',
    name='order_agent',
    description='Un agente que crea ordenes de compra de productos.',
    instruction='Debes crear ordenes de compra de productos. Para eso necesitas el codigo del producto y la cantidad a comprar. Para crear la orden debes usar la tool "order_producto"',
    tools=[order_producto]
)

# Define A2A agent card
order_agent_card = AgentCard(
    name="order_agent",
    description="Un agente que crea ordenes de compra de productos.",
    version="1.0.0",
    capabilities={},
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
)
a2a_app = to_a2a(order_agent, port=8001, agent_card=order_agent_card)