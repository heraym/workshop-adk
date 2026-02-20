import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Crear un directorio de prueba para que el agente acceda
# Obtener la ruta absoluta del directorio que contiene este script
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Definir la ruta para el espacio de trabajo del agente
AGENT_WORKSPACE_PATH = os.path.join(_CURRENT_DIR, "agent_workspace")

# Crear el directorio si no existe
if not os.path.exists(AGENT_WORKSPACE_PATH):
    os.makedirs(AGENT_WORKSPACE_PATH)
    # Crear un archivo ficticio dentro para que el agente lo encuentre
    with open(os.path.join(AGENT_WORKSPACE_PATH, "welcome.txt"), "w") as f:
        f.write("¡Hola desde el espacio de trabajo de su agente ADK!")

# Definir el Agente de Sistema de Archivos
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='filesystem_agent',
    instruction=f"""
    Usted es un asistente útil que puede interactuar con el sistema de archivos local de un usuario.
    Usted tiene restringido operar ÚNICAMENTE dentro del siguiente directorio: {AGENT_WORKSPACE_PATH}.
    Nunca intente acceder a archivos o directorios fuera de esta ruta.
    Cuando un usuario le pida listar archivos, use la herramienta 'list_directory'.
    Cuando un usuario le pida leer un archivo, use la herramienta 'read_file'.
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Confirmar automáticamente las solicitudes de instalación de npx
                        "@modelcontextprotocol/server-filesystem",
                        # IMPORTANTE: Esta DEBE ser una ruta absoluta.
                        AGENT_WORKSPACE_PATH,
                    ],
                ),
            ),
            # Opcional: Filtrar explícitamente qué herramientas se exponen al agente
            tool_filter=['list_directory', 'read_file']
        )
    ],
)