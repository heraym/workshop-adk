# agents/orchestrator_agent.py
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv


# Cargar variables de entorno desde el archivo .env
load_dotenv()


# Configurar el Cliente del Agente Remoto
# RemoteA2aAgent es el componente del lado del cliente que sabe cómo hablar con
# un servidor A2A. Lo configuramos con la URL de nuestro math_agent.
math_service = RemoteA2aAgent(
    name="math_service",
    description="Un servicio que puede realizar cálculos matemáticos como sumas.",
    agent_card=(
        f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)


# Definir el Agente Orquestador
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='orchestrator_agent',
    instruction="""
    Eres un orquestador. Resuelves problemas delegando tareas a
    servicios especializados.
    Si el usuario pide una adición o una suma, DEBES usar el 'math_service'.
    No realices la suma tú mismo.
    """,
    # El agente remoto se trata igual que un sub-agente
    sub_agents=[
        math_service
    ],
)