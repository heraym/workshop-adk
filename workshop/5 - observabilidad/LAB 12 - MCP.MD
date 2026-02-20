## H1  Habilitando su Agente ADK con Herramientas MCP

En este lab, vamos a ver como ampliar las capacidades de los
 agentes de Google ADK conectándolos a herramientas y servicios externos mediante el Protocolo de Contexto de Modelo (MCP). El MCP actúa como un adaptador universal, permitiendo que su agente se comunique con una amplia gama de herramientas preconstruidas sin necesidad de escribir código de integración personalizado para cada una.
Construiremos dos capacidades de agente distintas: una que interactúa con su sistema de archivos local y otra que utiliza Google Maps para proporcionar direcciones.


## H2 1. Configura tu entorno
Primero, preparemos tu entorno de desarrollo local. Crearemos una carpeta de proyecto dedicada, configuraremos un entorno virtual de Python para mantener nuestras dependencias aisladas e instalaremos el ADK.

Usaremos un solo comando de ADK para generar la estructura de un proyecto de agente completo basado en código.
Desde tu directorio adk-workshop-python (con el entorno virtual aún activo), ejecuta el siguiente comando:

`adk create --type=code mi_agente_file_tool`

Cuando solicita el modelo elijamos gemini-2.5-flash:

```Choose a model for the root agent:
1. gemini-2.5-flash
2. Other models (fill later)
Choose model (1, 2): 1 ```

Elijamos Vertex AI como backend
```1. Google AI
2. Vertex AI
Choose a backend (1, 2): 2


You need an existing Google Cloud account and project, check out this link for details:
https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai 
```

Elije proyecto y region:

```Enter Google Cloud project ID [xxxx-xxxxx-xxxxxxxx]: 
Enter Google Cloud region [us-central1]: 
```
 

## H2 2. Construyendo un Agente de Sistema de Archivos

Nuestro primer agente utilizará un servidor MCP local que proporciona herramientas para interactuar con el sistema de archivos. Este es un "hola mundo" perfecto para MCP porque se ejecuta completamente en su máquina y no requiere claves de API.

Crear el Código del Agente
Editemos el archivo llamado mi_agente_file_tool/agent.py y añada el siguiente código.

```
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
```

## H2 3. Probar el Agente 
Desde el directorio raíz de su proyecto ejecute la interfaz web de ADK.
adk web
El comando adk web descubrirá automáticamente el filesystem_agent dentro del paquete agents.
Abra su navegador web en http://127.0.0.1:8000.
Pruebe las siguientes instrucciones en la interfaz de chat:

¿Puedes listar los archivos en tu directorio?
Por favor, lee el contenido de welcome.txt

Debería ver que el agente enumera correctamente el archivo y luego lee su contenido, demostrando que está utilizando con éxito las herramientas proporcionadas por el servidor MCP del sistema de archivos.

*** ¡Felicitaciones! ***
Ha habilitado con éxito sus agentes ADK con potentes herramientas externas utilizando el Protocolo de Contexto de Modelo.

