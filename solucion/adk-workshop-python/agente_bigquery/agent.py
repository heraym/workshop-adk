import os
import google.auth
import google.auth.transport.requests
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# URL del servidor MCP de BigQuery
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"

def get_bigquery_mcp_toolset():
    """Configura y retorna un MCPToolset para BigQuery."""
    try:
        # Obtener credenciales ADC
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        # Refrescar el token para asegurarse de que sea válido
        credentials.refresh(google.auth.transport.requests.Request())
        oauth_token = credentials.token

        if not project_id:
            project_id = os.getenv("PROJECT_ID")

        if not oauth_token:
            raise Exception("No se pudo obtener el token OAuth.")
        if not project_id:
            raise Exception("No se pudo determinar el Project ID.")

        # Headers necesarios para la autenticación con el MCP Server
        headers = {
            "Authorization": f"Bearer {oauth_token}",
            "x-goog-user-project": project_id  # Especifica el proyecto para facturación y cuotas
        }

        # Parámetros de conexión HTTP
        connection_params = StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=headers
        )

        # Crear el Toolset MCP
        tools = MCPToolset(connection_params=connection_params)
        print("MCP Toolset para BigQuery configurado correctamente.")
        return tools

    except Exception as e:
        print(f"Error configurando el BigQuery MCP Toolset: {e}")
        return None

# Crear la instancia del Toolset
bigquery_toolset = get_bigquery_mcp_toolset()



# Definir el Agente LLM
if bigquery_toolset:
    root_agent = LlmAgent(
        model='gemini-2.5-flash', # O el modelo que prefieras
        name='bigquery_agent',
        instruction="Eres un asistente de datos útil. Responde preguntas utilizando las herramientas de BigQuery proporcionadas para consultar la base de datos. Usa el proyecto genai-demos-432617 y la tabla test",
        tools=[bigquery_toolset]
    )
    print("Agente ADK creado con éxito con herramientas de BigQuery.")

    # Aquí podrías iniciar la interacción con el agente, por ejemplo, usando adk web
    # Ejemplo de cómo iniciar la UI web de ADK:
    # Asegúrate de tener esta parte en un archivo main.py y ejecutar desde la terminal:
    # >> adk web
else:
    print("No se pudo crear el agente porque el Toolset de BigQuery falló.")