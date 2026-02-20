from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv


# Cargar variables de entorno desde el archivo .env
load_dotenv()


# Definir la Habilidad Principal del Agente
def add(a: int, b: int) -> int:
    """Suma dos números enteros."""
    print(f"[math_agent] Ejecutando add({a}, {b})")
    return a + b


# Definir el Agente ADK
math_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='math_agent',
    instruction="Eres un experto en matemáticas. Usas la herramienta 'add' para realizar sumas.",
    tools=[
        FunctionTool(add)
    ],
)


# Exponer el Agente vía A2A
# La función to_a2a() envuelve nuestro agente en una aplicación de servidor web (FastAPI)
# que habla el protocolo A2A. También genera automáticamente la
# tarjeta de agente requerida para que otros agentes sepan cómo hablar con él.

a2a_app = to_a2a(math_agent, port=8001)