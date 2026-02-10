## H1 Laboratorio: Despliegue de Agentes ADK en Vertex AI Agent Engine

Has construido y probado localmente tu agente de IA con el Kit de Desarrollo de Agentes (ADK). Ahora es el momento de dar el siguiente paso: desplegarlo en un entorno escalable y listo para producción.

Este lab  proporciona una guía práctica para desplegar tu agente ADK en Vertex AI Agent Engine. Agent Engine es un servicio de Google Cloud totalmente gestionado diseñado para ejecutar, administrar y escalar agentes de IA. Se encarga de la infraestructura subyacente, la contenedorización y las redes, permitiéndote centrarte en la construcción de la lógica inteligente del agente.

Al final de este laboratorio, habrás tomado un agente Python local y lo habrás convertido en un *endpoint* seguro y consultable en Google Cloud.


## H2 1. Configuración del Proyecto

Primero, vamos a configurar nuestro directorio de proyecto local e instalar las bibliotecas necesarias.

1.  Crea un nuevo directorio para el laboratorio y navega hasta él.

`mkdir -p adk-agent-engine-lab/agents`

1.  `cd adk-agent-engine-lab/agents`
2.  Instala los paquetes de Python requeridos. Los extras `[adk,agent_engines]` son cruciales para este laboratorio.
3.  `pip install --upgrade --quiet "google-cloud-aiplatform[adk,agent_engines]"`
4.  Crea los archivos para nuestro proyecto. Tendremos un archivo para la lógica del agente y otro para el *script* de despliegue.
5.  `touch agent.py __init__.py`

## H2 2. Crea el Agente ADK

Ahora, vamos a definir un agente meteorológico simple. Este agente tendrá una única herramienta para obtener un informe meteorológico para una ciudad determinada.

1.  Abre `agent.py` y añade el siguiente código:

``` 
# agent.py`

from google.adk.agents import Agent

def get_weather(city: str) -> dict:


"""Retrieves the current weather for a specified city."""

print(f"Tool call: get_weather(city='{city}')")

if city.lower() == "new york":

    return {

        "status": "success",

        "report": "The weather in New York is sunny with a temperature of 25°C.",

    }

return {"status": "error", "message": f"Weather for '{city}' not found."}

# The 'root_agent' variable is what the ADK framework discovers.

root_agent = Agent(
  name="weather_agent",
  model="gemini-2.5-flash",
  description="An agent that can provide weather reports.",
  instruction="You must use the available tools to find an answer.",
  tools=[get_weather],
)
``` 


2.  Abre `__init__.py` y añade la siguiente línea. Esto le dice a Python que el directorio es un paquete y hace que el agente sea detectable.

``` 
# __init__.py
from . import agent
``` 


## H2 3. Escribe el Script de Despliegue

Esta es la parte central del laboratorio. Escribiremos un *script* de Python que utiliza el SDK de Vertex AI para empaquetar y desplegar nuestro agente en Agent Engine.

Ve debajo de `adk-agent-engine-lab` y abre `deploy.py` y añade el siguiente código:

``` 
# deploy.py

import os
import vertexai
from vertexai import agent_engines

# Import the agent we defined in the other file

from agents.agent import root_agent

# Configuration

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"

BUCKET_URI = f"gs://{BUCKET_NAME}"

def deploy_agent():

"""Packages and deploys the ADK agent to Vertex AI Agent Engine."""

  print(f"Initializing Vertex AI for project '{PROJECT_ID}' in '{LOCATION}'...")
  
  # Initialize the Vertex AI SDK
  vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=BUCKET_URI,
  )

  # Wrap the ADK agent in an AdkApp object
  # This makes it compatible with Agent Engine and handles session management.

  print("Wrapping agent in AdkApp...")

  app = agent_engines.AdkApp(
    agent=root_agent,
  )


  # Deploy the application
  # This packages the code, builds a container, and deploys it.
  # This process can take several minutes.

  print("Starting deployment to Agent Engine... This may take 5-10 minutes.")

  remote_app = agent_engines.create(
     agent_engine=app,
     # Tell Agent Engine which libraries to install in the managed environment.
     requirements=["google-cloud-aiplatform[adk,agent_engines]"],
     display_name="My Weather Agent", 
     extra_packages=["agents"]
  )

  print("\n--- Deployment finished! ---")
  print(f"Deployed Agent Resource Name: {remote_app.resource_name}")

if __name__ == "__main__":
  deploy_agent()

```

## H2 4. Ejecuta el Script de Despliegue

Con tu agente y *script* de despliegue listos, ejecuta el despliegue desde tu terminal.

`python deploy.py`

Verás registros de salida a medida que el *script* inicializa el SDK, envuelve el agente y luego comienza el proceso de despliegue. El despliegue implica construir una imagen de contenedor, enviarla a un registro y aprovisionar el servicio en Agent Engine. Sé paciente, ya que esto puede tardar de 5 a 10 minutos.

Una vez completado con éxito, el *script* imprimirá el Nombre de Recurso único para tu agente desplegado. Copia este valor, ya que lo necesitarás en el siguiente paso para probar el agente.

`--- Deployment finished! ---`

`Deployed Agent Resource Name: projects/1234567890/locations/us-central1/reasoningEngines/9876543210`

También puedes ver tu agente desplegado en Google Cloud Console navegando a la página [Vertex AI \> Agent Engine](https://console.cloud.google.com/vertex-ai/agents/agent-engines).

## H2 5: Prueba el Agente Desplegado

Ahora que el agente está activo, vamos a escribir un *script* cliente simple para interactuar con él.

1.  Crea un nuevo archivo llamado `test_deployed_agent.py`.
2.  Añade el siguiente código, reemplazando el marcador de posición con el Nombre de Recurso que copiaste del paso anterior.

```
# test_deployed_agent.py

import asyncio
from vertexai import agent_engines

# TODO: Paste the Resource Name from the deployment script output here

AGENT_RESOURCE_NAME = "projects/224237244779/locations/us-central1/reasoningEngines/2686224554400940032"

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

  prompt = "What's the weather like in New York?"
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
2.  Ejecuta el *script* de prueba desde tu terminal:
3.  `python test_deployed_agent.py`

Verás que el *script* se conecta a tu agente, crea una sesión y luego imprime el *stream* de eventos a medida que el agente procesa tu solicitud. Este *stream* incluye la llamada inicial a la herramienta, la respuesta de la herramienta y la respuesta de texto final del LLM.

```
--- Agent Response Stream ---
{'role': 'model', 'parts': [{'function_call': {'name': 'get_weather', 'args': {'city': 'New York'}, 'id': '...'}}]}
{'role': 'user', 'parts': [{'function_response': {'name': 'get_weather', 'response': {'report': 'The weather in New York is sunny...', 'status': 'success'}, 'id': '...'}}]}
{'role': 'model', 'parts': [{'text': 'The weather in New York is sunny with a temperature of 25°C.'}]}
--- End of Stream ---
```

## H2  6. Limpieza

Para evitar incurrir en cargos, es importante eliminar la instancia de Agent Engine desplegada cuando hayas terminado.

1.  Puedes hacer esto programáticamente creando un *script* `cleanup.py`:

```
# cleanup.py

from vertexai import agent_engines

AGENT_RESOURCE_NAME = "projects/1234567890/locations/us-central1/reasoningEngines/9876543210" # Pega tu nombre de recurso aquí

print(f"Deleting agent: {AGENT_RESOURCE_NAME}")
remote_app = agent_engines.get(AGENT_RESOURCE_NAME)
remote_app.delete(force=True) # force=True también elimina recursos hijos como sesiones`

print("Agent deleted.")

```
2.  Luego ejecuta `python cleanup.py`.

Alternativamente, puedes eliminar el agente directamente desde la página [Vertex AI \> Agent Engine](https://console.cloud.google.com/vertex-ai/agents/agent-engines) en Google Cloud Console.

1.  Elimina el *bucket* de GCS:
2.  `gsutil rm -r $STAGING_BUCKET`

## **¡Felicidades\!**

¡Has desplegado, probado y limpiado con éxito un agente de Google ADK en Vertex AI Agent Engine\!
