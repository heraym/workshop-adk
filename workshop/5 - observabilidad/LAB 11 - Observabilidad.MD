## H1 Observabilidad para Agentes ADK en Agent Engine con Cloud Trace

Una vez que se implementa un agente, ¿cómo sabes lo que *realmente* está haciendo? Cuando un usuario reporta una respuesta lenta o incorrecta, ¿cómo depuras la compleja cadena de llamadas a LLM, ejecuciones de herramientas y lógica interna?

La respuesta es la observabilidad. Este lab se centra en una piedra angular de la observabilidad: el rastreo distribuido. Aprenderás cómo habilitar el rastreo para tu agente ADK en Vertex AI Agent Engine con una sola línea de código. Luego, consultaremos nuestro agente implementado y nos sumergiremos en Google Cloud Trace para visualizar su ruta de ejecución completa, desde la solicitud inicial del usuario hasta la respuesta final.

## H2 1. Configuración del Proyecto

Es necesario habilitar las APIs de Cloud Trace

``` 
    gcloud services enable aiplatform.googleapis.com cloudtrace.googleapis.com
    
```
(Reemplaza YOUR\_PROJECT\_ID con el ID real de tu proyecto).
**Bucket de Google Cloud Storage (GCS):** Necesitas un bucket de GCS para el *staging* de los archivos de implementación.

Crea un nuevo directorio para el laboratorio e ingrésalo.

``` 
mkdir -p adk-tracing-lab/agents
cd adk-tracing-lab/agents

```

Instala las bibliotecas necesarias desde PyPI.
``` 
pip install --upgrade --quiet "google-cloud-aiplatform[adk,agent_engines]"
    
```

Crea los archivos para nuestro proyecto. Tendremos un archivo para la lógica del agente y otro para el script de implementación.
``` 
touch agent.py __init__.py
    
```

## H2 2 Crear el Agente ADK

Usaremos el mismo agente meteorológico simple del laboratorio LAB9. Su estructura de una sola herramienta es perfecta para demostrar un rastro limpio y fácil de entender.

Abre `agent.py` y agrega el siguiente código:

``` python
# agent.py

from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather for a specified city."""
    print(f"Tool call: get_weather(city='{city}')")
    if city.lower() == "paris":
        return {
            "status": "success",
            "report": "The weather in Paris is cloudy with a temperature of 18°C.",
        }
    return {"status": "error", "message": f"Weather for '{city}' not found."}

root_agent = Agent(
    name="weather_agent_traced",
    model="gemini-2.5-flash",
    description="An agent that can provide weather reports and is traced.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)

```

A continuación, abre `__init__.py` y agrega esta línea para que el agente sea detectable como un paquete de Python:

``` python
# __init__.py

from . import agent

```

## H2 3. Implementar el Agente con Rastreo Habilitado

Duración: 15:00

Este es el paso clave del laboratorio. Escribiremos un script de implementación que es casi idéntico a una implementación estándar, pero con un cambio crítico.

Luego crea el archivo `deploy_with_tracing.py` en `adk-tracing-lab` y agrega el siguiente código:

``` python
# deploy_with_tracing.py

import os
import vertexai
from vertexai import agent_engines
from agents.agent import root_agent

# Configuration
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"
BUCKET_URI = f"gs://{BUCKET_NAME}"

def deploy_agent():
    """Deploys the ADK agent with Cloud Trace enabled."""
    print(f"Initializing Vertex AI for project '{PROJECT_ID}'...")
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=BUCKET_URI,
    )

    print("Wrapping agent in AdkApp with tracing enabled...")

    # --- ESTA ES LA CLAVE ---
    # El flag `enable_tracing=True` configura automáticamente el agente
    # para enviar rastros de OpenTelemetry a Google Cloud Trace.
    app = agent_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    # -----------------------

    print("Starting deployment... This may take 5-10 minutes.")
    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        display_name="Traced Weather Agent",
        extra_packages=["agents"]
    )

    print("\n--- Deployment finished! ---")
    print(f"Deployed Agent Resource Name: {remote_app.resource_name}")

if __name__ == "__main__":
    deploy_agent()

```

¿Qué hace `enable_tracing=True`?

Este simple *flag* instruye a Agent Engine para que configure automáticamente el *framework* estándar de la industria [OpenTelemetry](https://opentelemetry.io/) dentro del entorno administrado de tu agente. Configura los exportadores y la propagación de contexto necesarios para capturar detalles de tiempo y metadatos de cada paso de la ejecución de tu agente y envía estos datos de forma segura al servicio Google Cloud Trace de tu proyecto.

Ahora, ejecuta el script desde tu terminal:

``` 
python deploy_with_tracing.py

```

Espera a que se complete la implementación. Puede tardar varios minutos. Una vez finalizado, copia el nombre de recurso del agente implementado (*Deployed Agent Resource Name*). Lo necesitarás para el siguiente paso.

## H2 4. Generar Rastros Consultando el Agente**

Un sistema de observabilidad solo es útil si tiene datos. Enviemos una solicitud a nuestro agente recién implementado para generar un rastro.

Crea el archivo `query_agent.py` en `adk-tracing-lab`.
Agrega el siguiente código, pegando el Nombre del Recurso de la salida del paso anterior.


``` python
# query_agent.py

import asyncio
from vertexai import agent_engines

# TODO: Pega el Nombre del Recurso de la salida del script de implementación aquí
AGENT_RESOURCE_NAME = "projects/your-gcp-project-id/locations/us-central1/reasoningEngines/1234567890"

async def main():
    """Connects to the deployed agent and sends a query to generate a trace."""
    print(f"Connecting to remote agent: {AGENT_RESOURCE_NAME}")
    remote_app = agent_engines.get(AGENT_RESOURCE_NAME)

    print("Creating new remote session...")
    session = await remote_app.async_create_session(user_id="trace-user-001")

    prompt = "How is the weather in Paris?"
    print(f"Sending prompt: '{prompt}'")

    final_response = ""
    async for event in remote_app.async_stream_query(
        user_id="trace-user-001",
        session_id=session["id"],
        message=prompt,
    ):
        print(event)
    print("\nTrace data has been sent to Google Cloud Trace.")

if __name__ == "__main__":
    asyncio.run(main())

```

Ejecuta el script para enviar una solicitud.
``` 
python query_agent.py
    
```

Ahora has ejecutado con éxito tu agente remoto y, en segundo plano, se ha enviado un rastro detallado de esa ejecución a Google Cloud.

## H2 5. Inspeccionar Rastros en el Explorador de Cloud Trace

Ahora viene la recompensa. Vamos a visualizar lo que hizo nuestro agente.

1.  Abre el [Explorador de Google Cloud Trace](https://cloud.google.com/trace/docs/trace-explorer) en tu navegador.
2.  Puede que tarde uno o dos minutos en ingerirse y ser visible el dato de rastro. Deberías ver una nueva entrada en la lista de rastros. Haz clic en ella para abrir la vista detallada.
3.  Ahora verás un diagrama de cascada. Esta es una línea de tiempo de la ejecución de tu agente, desglosada en operaciones distintas llamadas "spans" (*tramos*).

**Interpretación del Rastro**

  * **Parent Span** (`/v1/...:query`): Este es el *span* de nivel superior que representa la solicitud completa a tu *endpoint* del agente implementado. Su duración es el tiempo total que el usuario esperó por una respuesta.
  * **agent\_run**: Este *span* representa la ejecución de la lógica de tu agente ADK.
  * **call\_llm** (Hijo de `agent_run`): Esto muestra el tiempo exacto que se dedicó a la llamada de red al modelo Gemini. Al hacer clic en este *span*, se revelan metadatos como el nombre del modelo.
  * **execute\_tool** (Hijo de `agent_run`): Esto muestra la ejecución de tu función `get_weather`. Captura cuánto tardó en ejecutarse el código de tu herramienta personalizada.

Esta vista jerárquica es invaluable. Si tu agente fuera lento, podrías ver inmediatamente si el cuello de botella estaba en la llamada a LLM, en una de tus herramientas o en la propia sobrecarga del agente.

## H2 6. Limpieza

Para evitar incurrir en costos continuos, elimina el agente implementado y el bucket de GCS.

1.  Elimina la instancia de Agent Engine desde la Cloud Console o ejecutando un script de limpieza.
2.  Elimina el bucket de GCS:
    ``` 
    gsutil rm -r $STAGING_BUCKET
    
    ```

## **¡Felicidades\!**

Has habilitado e inspeccionado con éxito la observabilidad de nivel de producción para un agente ADK implementado.
