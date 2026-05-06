## H1  Compila e implementa un servidor de MCP remoto en Cloud Run


## H2 1. Instala uv como paquete de administracion de python

Primero hay que instalar uv (paquete de administracion de python) siguiendo esta documentacion:
https://docs.astral.sh/uv/getting-started/installation/#standalone-installer


## H2 2. Armar proyecto de python

Creamos un directorio:
  mkdir mcp-on-cloudrun
  cd mcp-on-cloudrun

Creamos un proyecto de Python con la herramienta uv para generar un archivo pyproject.toml:

  uv init --name "mcp-on-cloudrun" --description "Ejemplo de implementar un servidor MCP en Cloud Run" --bare --python 3.10


Crea los siguientes archivos nuevos adicionales:

- server.py para el código fuente del servidor de MCP
- test_server.py para probar el servidor remoto
- Un Dockerfile para implementar en Cloud Run

El directorio de tu proyecto debe contener la siguiente estructura:

├── mcp-on-cloudrun
│   ├── pyproject.toml
│   ├── server.py
│   ├── test_server.py
│   └── Dockerfile

## H2 3. Crea un servidor de MCP para operaciones matemáticas

Para proporcionar un contexto valioso para mejorar el uso de LLMs con MCP, configura un servidor de MCP matemático con FastMCP. FastMCP proporciona una forma rápida de compilar servidores y clientes de MCP con Python.

Sigue estos pasos para crear un servidor de MCP para operaciones matemáticas, como la suma y la resta.

Ejecuta el siguiente comando para agregar FastMCP como una dependencia en el archivo pyproject.toml:

`uv add fastmcp==2.13.1 --no-sync`

Agrega el siguiente código fuente del servidor de MCP matemático en el archivo server.py:

```
import asyncio
import logging
import os

from fastmcp import FastMCP 

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("MCP Server on Cloud Run")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Use this to add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    logger.info(f">>> 🛠️ Tool: 'add' called with numbers '{a}' and '{b}'")
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Use this to subtract two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference of the two numbers.
    """
    logger.info(f">>> 🛠️ Tool: 'subtract' called with numbers '{a}' and '{b}'")
    return a - b

if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="streamable-http",
            host="0.0.0.0",
            port=os.getenv("PORT", 8080),
        )
    )
```

Incluye el siguiente código en el Dockerfile para usar la herramienta uv para ejecutar el archivo server.py:


```
# Use the official Python image
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the project into /app
COPY . /app
WORKDIR /app

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN uv sync

EXPOSE $PORT

# Run the FastMCP server
CMD ["uv", "run", "server.py"]

```

## H2 3. Implementa en Cloud Run

Para implementar un servidor de MCP empaquetado como una imagen de contenedor, sigue estas instrucciones.

Crea un repositorio de Artifact Registry para almacenar la imagen de contenedor:


```
gcloud artifacts repositories create remote-mcp-servers \
--repository-format=docker \
--location=us-central1 \
--description="Repository for remote MCP servers" \
--project=PROJECT_ID
```

Compila la imagen de contenedor y envíala a Artifact Registry con Cloud Build:

```
gcloud builds submit --region=us-central1 --tag us-central1-docker.pkg.dev/PROJECT_ID/remote-mcp-servers/mcp-server:latest
```

Implementa la imagen de contenedor del servidor de MCP en Cloud Run:

```
gcloud run deploy mcp-server \
--image us-central1-docker.pkg.dev/PROJECT_ID/remote-mcp-servers/mcp-server:latest \
--region=us-central1 \
--no-allow-unauthenticated
```

## H2 4. Probar servicio MCP

Para probar el servicio asegurate que la cuenta de servicio o usuario con el que ejecutas tiene permisos para ejecutar el servicio de Cloud Run. 

Crea un archivo de prueba llamado test_server.py y agrega el siguiente código:

```
import asyncio

from fastmcp import Client


async def test_server():
    # Test the MCP server using streamable-http transport.
    # Use "/sse" endpoint if using sse transport.
    async with Client("https://<url-cloud-run>/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        for tool in tools:
            print(f">>> 🛠️  Tool found: {tool.name}")
        # Call add tool
        print(">>> 🪛  Calling add tool for 1 + 2")
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(f"<<< ✅ Result: {result.content[0].text}")
        # Call subtract tool
        print(">>> 🪛  Calling subtract tool for 10 - 3")
        result = await client.call_tool("subtract", {"a": 10, "b": 3})
        print(f"<<< ✅ Result: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(test_server())
```

En una terminal nueva, ejecuta el servidor de prueba:

` uv run test_server.py `

Deberías ver el siguiente resultado:

```
 🛠️ Tool found: add
 🛠️ Tool found: subtract
 🪛 Calling add tool for 1 + 2
 ✅ Result: 3
 🪛 Calling subtract tool for 10 - 3
 ✅ Result: 7

 ```

## H2 5. Agente que usa servicio MCP

Vamos a crear un agente que use el servidor MCP. 
Para eso vamos al directorio anterior (adk-workshop-python o con el que hayamos arrancado este laboratorio) y ejecuta el siguiente comando:

`adk create --type=code mi_agente_matematico`

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

Agent created in /home/user/workshop-adk/solucion/adk-workshop-python/mi_agente_matematico:
- .env
- __init__.py
- agent.py
```

El ADK ha creado un nuevo directorio llamado mi_agente_matematico. Examinemos la estructura de archivos generada:

mi_agente_matematico/
├── .env
- __init__.py
└── agent.py

**agent.py:** Este es el punto de entrada para nuestro agente. Escribiremos nuestro código Python aquí para definir y configurar el agente.
**.env:** Este es un archivo especial para almacenar secretos, como nuestra clave de API.


Esta estructura limpia proporciona el punto de partida perfecto para construir un agente basado en Python.

## H2 6. Configura el agente que usa el servidor MCP
Con el proyecto creado, escribamos el código para nuestro agente.
Ahora, abre el archivo mi_agente_matematico/agent.py. Aquí es donde definirás programáticamente la personalidad y el propósito de tu agente.
Reemplaza el contenido del archivo con el siguiente código Python.  


``` 
import os
import google.auth
import google.auth.transport.requests
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# URL del servidor MCP Matematico
MATE_MCP_URL = "<url-cloud-run>/mcp"

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
```

 
## H2 5. Ejecuta e interactúa con tu agente

Ahora probemos el agente. Vamos a deployar el agente en Agent Engine. 
Para eso vamos a ejecutar lo siguiente:

```
export GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=TRUE
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=TRUE

adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --trace_to_cloud \
        --otel_to_cloud \
        --display_name="Agente Matematico" \
        mi_agente_matematico
```

Ahora que el agente está activo, vamos a escribir un cliente simple para interactuar con él.

1.  Crea un nuevo archivo llamado `test_agente.py`.
2.  Añade el siguiente código, reemplazando el nombre de recurso de Agent Engine que te genero el deploy

```
# test_deployed_agent.py

import asyncio
from vertexai import agent_engines

# TODO: Paste the Resource Name from the deployment script output here

AGENT_RESOURCE_NAME = "<nombre_recurso_agent_engine>"

async def main():

  """Connects to the deployed agent and sends a query."""
  print(f"Connecting to remote agent: {AGENT_RESOURCE_NAME}")
  
  # Get a client handle to the remote application

  remote_app = agent_engines.get(AGENT_RESOURCE_NAME)

  # Create a remote session to maintain conversation history
  print("Creating new remote session...")
  remote_session = await remote_app.async_create_session(user_id="test-user-123")
  print(f"Session created with ID: {remote_session['id']}")

  # Send a query to the agent

  prompt = "Cuanto es 5 + 5?"
  print(f"\nSending prompt: '{prompt}'")

  print("\n--- Agent Response Stream ---")
  async for event in remote_app.async_stream_query(
     user_id="test-user-123",
     session_id=remote_session["id"],
     message=prompt,
  ):

    print(event)
  print("--- End of Stream ---")


if __name__ == "__main__":
    asyncio.run(main())

```