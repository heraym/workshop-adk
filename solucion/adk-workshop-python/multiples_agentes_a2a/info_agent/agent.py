from google.adk.agents.llm_agent import Agent
from a2a.types import AgentCard
# Agent Engine
from vertexai.agent_engines.templates.a2a import A2aAgent, create_agent_card
from a2a.client import ClientConfig, ClientFactory
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a import types as a2a_types
from a2a.utils import TransportProtocol

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

root_agent = Agent(
    model='gemini-2.5-flash',
    name='info_agent',
    description='Un agente que provee informacion de los productos.',
    instruction='Debes proveer informacion de los productos por los que te consultan. Para eso debes usar la tool "info_producto"',
    tools=[info_producto]
)

# Define a skill - a specific capability your agent offers
# Agents can have multiple skills for different tasks
info_agent_skill = a2a_types.AgentSkill(
    # Unique identifier for this skill
    id="info_prod",
    # Human-friendly name
    name="Info de Productos",
    # Detailed description helps clients understand when to use this skill
    description="Obtener informacion de productos",
    # Tags for categorization and discovery
    # These help in agent marketplaces or registries
    tags=["info", "productos", "precio"],
    # Examples show clients what kinds of requests work well
    # This is especially helpful for LLM-based clients
    examples=[
        "Cual es el precio del producto producto1?",
        "Que es el producto producto2?",
    ],
    # Optional: specify input/output modes
    # Default is text, but could include images, files, etc.
    input_modes=["text/plain"],
    output_modes=["text/plain"],
)

# Use the helper function to create a complete Agent Card
info_agent_card = create_agent_card(
    agent_name="Info Agent",
    description="Agente que provee info de productos",
    skills=[info_agent_skill],
)


#a2a_app = to_a2a(root_agent, agent_card=info_agent_card)