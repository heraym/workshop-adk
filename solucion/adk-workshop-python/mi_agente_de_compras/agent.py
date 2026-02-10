# mi_agente_de_compras/agent.py (Código Final)

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def view_shopping_list(tool_context: ToolContext) -> str:
    """Muestra los artículos actualmente en la lista de compras."""
    print("Executing tool: view_shopping_list")
    current_list = tool_context.state.get("shopping_list", [])
    if not current_list:
        return "The shopping list is currently empty."
    return "Here is your shopping list:\n- " + "\n- ".join(current_list)

def add_to_shopping_list(item: str, tool_context: ToolContext) -> str:
    """Añade un solo artículo a la lista de compras."""
    print(f"Executing tool: add_to_shopping_list with item '{item}'")
    current_list = tool_context.state.get("shopping_list", [])
    if item.lower() not in [i.lower() for i in current_list]:
        current_list.append(item)
    tool_context.state["shopping_list"] = current_list
    return f"'{item}' has been added to the list."

async def save_list_as_artifact(callback_context: CallbackContext):
    print("Callback triggered: save_list_as_artifact")
    shopping_list = callback_context.state.get("shopping_list", [])
    if not shopping_list:
        print("List is empty, not saving artifact.")
        return
    file_content = "My Shopping List:\n\n- " + "\n- ".join(shopping_list)
    artifact_part = types.Part(text=file_content)
    try:
        version = await callback_context.save_artifact(
                filename="shopping_list.txt",
                artifact=artifact_part
        )
        print(f"✅ Successfully saved shopping_list.txt as version {version}")
    except ValueError as e:
        print(f"🔴 Error saving artifact: {e}. Is an ArtifactService configured in your runner?")

# Definición del Agente
root_agent: Agent = Agent(
    model="gemini-2.5-flash",
    name="ShoppingListAgent",
    instruction="""Eres un asistente de lista de compras.
    - Usa la herramienta 'add_to_shopping_list' para agregar artículos.
    - Usa la herramienta 'view_shopping_list' para ver la lista actual.
    - Reconoce cuando se ha agregado un artículo.
    - Cuando el usuario pida "guardar la lista", responde con "OK, guardando tu lista."
    """,
    tools=[
        FunctionTool(func=view_shopping_list),
        FunctionTool(func=add_to_shopping_list),
    ],
    after_agent_callback=save_list_as_artifact,
)