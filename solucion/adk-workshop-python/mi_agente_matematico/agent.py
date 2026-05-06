import os
import google.auth
import google.auth.transport.requests
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# URL del servidor MCP Matematico
MATE_MCP_URL = "https://mcp-server-224237244779.us-central1.run.app/mcp"

def get_mate_mcp_toolset():
    """Configura y retorna un MCPToolset para Matematica."""
    # Parámetros de conexión HTTP
    connection_params = StreamableHTTPConnectionParams(
         url=MATE_MCP_URL,
    )

    # Crear el Toolset MCP
    tools = MCPToolset(connection_params=connection_params)
    print("MCP Toolset para Matematica configurado correctamente.")
    return tools
    
# Crear la instancia del Toolset
mate_toolset = get_mate_mcp_toolset()



# Definir el Agente LLM
if mate_toolset:
    root_agent = LlmAgent(
        model='gemini-2.5-flash', # O el modelo que prefieras
        name='mate_agent',
        instruction="Eres un asistente matematico que responde preguntas sobre calculos matematicos. Responde preguntas utilizando las herramientas de Matematica proporcionadas.",
        tools=[mate_toolset]
    )
    print("Agente ADK creado con éxito con herramientas de Matematica.")

    # Aquí podrías iniciar la interacción con el agente, por ejemplo, usando adk web
    # Ejemplo de cómo iniciar la UI web de ADK:
    # Asegúrate de tener esta parte en un archivo main.py y ejecutar desde la terminal:
    # >> adk web
else:
    print("No se pudo crear el agente porque el Toolset de Matematica falló.")