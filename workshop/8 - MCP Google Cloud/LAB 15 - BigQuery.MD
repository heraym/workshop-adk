## H1  Usando MCP Server de BigQuery con ADK


## H2 1. Permisos para usar MCP Server de BigQuery


Para obtener los permisos que necesitas para usar el servidor de MCP de BigQuery, pídele a tu administrador que te otorgue los siguientes roles de IAM en el proyecto en el que deseas usar el servidor de MCP de BigQuery:

Realiza llamadas a la herramienta de MCP: Usuario de la herramienta de MCP (roles/mcp.toolUser)
Ejecutar trabajos de BigQuery: Usuario de trabajo de BigQuery (roles/bigquery.jobUser)
Consultar datos de BigQuery: Visualizador de datos de BigQuery (roles/bigquery.dataViewer)

## H2 2. Autenticacion y Autorizacion

Los servidores de MCP de BigQuery usan el protocolo OAuth 2.0 con IAM para la autenticación y la autorización. Se admiten todas las Google Cloud identidades para la autenticación en los servidores de MCP.

El servidor de MCP de BigQuery no acepta claves de API.

## H2 3. Crea un agente

Ahora la magia. Usaremos un solo comando de ADK para generar la estructura de un proyecto de agente completo basado en código.
Desde tu directorio adk-workshop-python (con el entorno virtual aún activo), ejecuta el siguiente comando:

`adk create --type=code agente_bigquery`

Cuando solicita el modelo elijamos gemini-2.5-flash:

```
Choose a model for the root agent:
1. gemini-2.5-flash
2. Other models (fill later)
Choose model (1, 2): 1  

Elijamos Vertex AI como backend
1. Google AI
2. Vertex AI
Choose a backend (1, 2): 2


You need an existing Google Cloud account and project, check out this link for details:
https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai 
```

Elije proyecto y region:

```
Enter Google Cloud project ID [xxxx-xxxx-xxxx]: 
xxxx-xxxx-xxxx
Enter Google Cloud region [us-central1]: 
us-central1
```

## H2 4. Configura tu agente


Configura un cliente de MCP para que use el servidor de MCP de BigQuery
Los programas host, como Claude o Gemini CLI, pueden crear instancias de clientes de MCP que se conectan a un solo servidor de MCP. Un programa host puede tener varios clientes que se conectan a diferentes servidores de MCP. Para conectarse a un servidor de MCP, el cliente de MCP debe conocer, como mínimo, la URL del servidor de MCP.

En tu host, busca una forma de conectarte a un servidor de MCP. Se te solicitará que ingreses detalles sobre el servidor, como su nombre y URL.

Para el servidor MCP de BigQuery, ingresa lo siguiente según sea necesario:

Nombre del servidor: Servidor de MCP de BigQuery
URL del servidor o Extremo: https://bigquery.googleapis.com/mcp
Transporte: HTTP
Detalles de autenticación: Tus Google Cloud credenciales, tu ID y secreto de cliente de OAuth, o bien la identidad y las credenciales de un agente

Los detalles de autenticación que elijas dependerán de cómo quieras autenticarte. Para obtener más información, consulta Cómo autenticarse en los servidores de MCP. https://docs.cloud.google.com/mcp/authenticate-mcp

En nuestro caso, vamos a incluir el siguiente codigo en el agente:

```
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
        instruction="Eres un asistente de datos útil. Responde preguntas utilizando las herramientas de BigQuery proporcionadas para consultar la base de datos.",
        tools=[bigquery_toolset]
    )
    print("Agente ADK creado con éxito con herramientas de BigQuery.")

    # Aquí podrías iniciar la interacción con el agente, por ejemplo, usando adk web
    # Ejemplo de cómo iniciar la UI web de ADK:
    # Asegúrate de tener esta parte en un archivo main.py y ejecutar desde la terminal:
    # >> adk web
else:
    print("No se pudo crear el agente porque el Toolset de BigQuery falló.")

```

Esto nos permite conectarse a cualquier ambiente de BigQuery y ejecutar consultas sobre este ambiente.