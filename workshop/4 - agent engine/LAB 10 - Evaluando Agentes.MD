## H1 Evaluación de Agentes ADK con Vertex AI



Este laboratorio te enseña a evaluar tus agentes ADK utilizando el **servicio de Evaluación de Vertex AI**. Este potente servicio gestionado te permite comparar el rendimiento del agente, definir métricas personalizadas basadas en modelos para la calidad y realizar un seguimiento de los resultados a lo largo del tiempo en un entorno persistente y compartible. Crearemos y evaluaremos un agente de investigación de productos, evaluando tanto el uso de herramientas como la calidad de su respuesta final.


## H2 1. Configuración e instalación del proyecto

Primero, configuremos nuestro directorio de proyecto e instalemos las bibliotecas de Python necesarias.

1.  Crea un nuevo directorio para tu proyecto y navega hasta él.
    
    ``` console
    mkdir adk-vertex-eval-lab
    cd adk-vertex-eval-lab
    
    ```

2.  Instala las bibliotecas requeridas. Necesitamos el ADK en sí y el SDK de Vertex AI con el extra `[evaluation]`.
    
    ``` console
    pip install --upgrade --quiet "google-adk" "google-cloud-aiplatform[evaluation]"
    
    ```

3.  Crea un nuevo archivo llamado `evaluate_agent.py`. Crearemos todo nuestro script de evaluación en este archivo.
    
    ``` console
    touch evaluate_agent.py
    
    ```

## H2 2. Crear el script de evaluación

Ahora llenaremos el script `evaluate_agent.py` paso a paso. Abre este archivo en tu editor de código favorito.

**Importaciones y configuración**

Agrega las importaciones necesarias y configura los detalles de tu proyecto de Google Cloud en la parte superior del script.

> **Importante:** Recuerda reemplazar los valores de marcador de posición para `PROJECT_ID` y `BUCKET_NAME` con los tuyos propios. El bucket se creará si no existe.

``` python
# evaluate_agent.py

import os
import json
import asyncio
import pandas as pd

import vertexai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService
from google.genai import types
from vertexai.preview.evaluation import EvalTask
from vertexai.preview.evaluation.metrics import (
    PointwiseMetric,
    PointwiseMetricPromptTemplate,
    TrajectorySingleToolUse,
)

# --- Configuration ---
# TODO: Replace with your Google Cloud project ID
PROJECT_ID = "your-gcp-project-id"
# TODO: Replace with a unique GCS bucket name
BUCKET_NAME = "your-unique-gcs-bucket-name"
LOCATION = "us-central1"
BUCKET_URI = f"gs://{BUCKET_NAME}"

# Set environment variables for ADK
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Configure Vertex AI Experiment name
EXPERIMENT_NAME = "adk-product-agent-evaluation"

print("Configuration loaded.")

```

**Definir el Agente y las Herramientas**

A continuación, define las herramientas y el agente ADK que queremos evaluar. Este agente actuará como un investigador de productos.

``` python
# evaluate_agent.py (append to file)

def get_product_details(product_name: str) -> str:
    """Gathers basic details about a product."""
    details = {
        "productx": "A cutting-edge smartphone with advanced camera features.",
        "producty": "High-performance running shoes designed for comfort and speed.",
    }
    return details.get(product_name.lower(), "Product details not found.")

def get_product_price(product_name: str) -> str:
    """Gathers the price of a product."""
    prices = {"productx": "500 USD", "producty": "100 USD"}
    return prices.get(product_name.lower(), "Product price not found.")

def build_agent():
    """Builds and returns the ADK agent."""
    return Agent(
        name="ProductResearchAgent",
        model="gemini-2.5-flash",
        description="An agent that performs product research.",
        instruction="You must use the available tools to answer user questions about product price or details.",
        tools=[get_product_details, get_product_price],
    )

print("Agent definition ready.")

```

**Crear una función de ejecución del agente (*Agent Runner Function*)**

El servicio de Evaluación de Vertex AI necesita una forma estándar de llamar a nuestro agente. Crearemos una función envoltorio que tome una instrucción del usuario, ejecute el agente ADK y devuelva la salida en un diccionario estructurado.

``` python
# evaluate_agent.py (append to file)

async def run_agent_async(prompt: str, agent: Agent) -> dict:
    """Runs the ADK agent for a given prompt and parses the output."""
    runner = Runner(
        agent=agent, app_name="eval_app", session_service=InMemorySessionService()
    )
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    await runner.session_service.create_session(
        app_name="eval_app", user_id="eval_user", session_id="eval_session"
    )

    events = [
        event
        async for event in runner.run_async(
            user_id="eval_user", session_id="eval_session", new_message=content
        )
    ]

    # Parse the event stream to find the final response and tool calls
    final_response = ""
    trajectory = []
    for event in events:
        if not getattr(event, "content", None) or not getattr(
            event.content, "parts", None
        ):
            continue
        for part in event.content.parts:
            if getattr(part, "function_call", None):
                info = {
                    "tool_name": part.function_call.name,
                    "tool_input": dict(part.function_call.args),
                }
                if info not in trajectory:
                    trajectory.append(info)
            if event.content.role == "model" and getattr(part, "text", None):
                final_response = part.text.strip()

    return {
        "response": final_response,
        "predicted_trajectory": json.dumps(trajectory),  # Must be a JSON string
    }

def agent_runner_sync(prompt: str):
    """Synchronous wrapper for the async agent runner."""
    # This is a bit of a trick to run our main async function from the sync context
    # of the evaluation library.
    agent = build_agent()
    result = asyncio.run(run_agent_async(prompt, agent))
    return result

print("Agent runner function defined.")

```

**Definir el conjunto de datos y las métricas de evaluación**

Ahora, define los datos de verdad fundamental y las métricas que usaremos para juzgar al agente.

``` python
# evaluate_agent.py (append to file)

def get_eval_dataset():
    """Creates a pandas DataFrame with evaluation data."""
    eval_data = {
        "prompt": [
            "How much does the productx cost?",
            "Tell me about producty.",
        ],
        "reference_trajectory": [
            [{"tool_name": "get_product_price", "tool_input": {"product_name": "productx"}}],
            [{"tool_name": "get_product_details", "tool_input": {"product_name": "producty"}}],
        ],
    }
    df = pd.DataFrame(eval_data)
    # The evaluation service expects the trajectory to be a JSON string
    df["reference_trajectory"] = df["reference_trajectory"].apply(json.dumps)
    return df

def get_eval_metrics():
    """Defines the metrics for the evaluation task."""
    # Metric 1: Check if the correct single tool was used.
    tool_metric = TrajectorySingleToolUse(tool_name="get_product_price")

    # Metric 2: A custom, model-based metric to judge response quality.
    criteria = {
        "Follows trajectory": (
            "Evaluate whether the agent's response logically follows from the "
            "sequence of actions it took. Does the response reflect the information "
            "gathered by the tool?"
        )
    }
    rating_rubric = {"1": "Follows trajectory", "0": "Does not follow trajectory"}

    prompt_template = PointwiseMetricPromptTemplate(
        criteria=criteria,
        rating_rubric=rating_rubric,
        input_variables=["prompt", "predicted_trajectory"],
    )

    response_metric = PointwiseMetric(
        metric="response_follows_trajectory",
        metric_prompt_template=prompt_template,
    )

    return [tool_metric, response_metric]

print("Evaluation dataset and metrics defined.")

```

**Definir el bloque de ejecución principal**

Finalmente, crea el bloque principal que inicializa Vertex AI, crea el bucket de GCS, configura la `EvalTask`, la ejecuta e imprime los resultados.

``` python
# evaluate_agent.py (append to file)

def main():
    """Main function to run the evaluation pipeline."""
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET_URI, experiment=EXPERIMENT_NAME)

    # Create GCS bucket if it doesn't exist
    print(f"Checking for GCS bucket: {BUCKET_URI}")
    os.system(f"gsutil ls -b {BUCKET_URI} || gsutil mb -l {LOCATION} {BUCKET_URI}")

    # Get dataset and metrics
    eval_dataset = get_eval_dataset()
    eval_metrics = get_eval_metrics()

    print("\n--- Starting Evaluation Task ---")
    print(f"Dataset has {len(eval_dataset)} rows.")

    # Create the evaluation task
    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=eval_metrics,
        experiment=EXPERIMENT_NAME
    )

    # Run the evaluation
    eval_result = eval_task.evaluate(
        runnable=agent_runner_sync,
        experiment_run_name="product-agent-run-1"
    )

    print("\n--- Evaluation Complete ---")
    print("Summary Metrics:")
    print(pd.DataFrame(eval_result.summary_metrics.items(), columns=["Metric", "Value"]))


if __name__ == "__main__":
    main()

```

## H2 3. Ejecutar el script de evaluación

Tu script `evaluate_agent.py` ya está completo. Ejecútalo desde tu terminal.

``` console
python evaluate_agent.py

```

El script hará lo siguiente:

1.  Inicializar Vertex AI y crear el bucket de GCS.
2.  Iniciar la tarea de evaluación. Esto puede tardar unos minutos ya que el servicio necesita poner en marcha recursos y llamar al LLM tanto para la lógica del agente como para la evaluación de métricas basada en modelos.
3.  Imprimir las métricas resumidas en tu consola cuando termine.

Deberías ver una salida similar a esta:

``` console
Configuration loaded.
Agent definition ready.
Agent runner function defined.
Evaluation dataset and metrics defined.
Checking for GCS bucket: gs://your-unique-gcs-bucket-name
Creating gs://your-unique-gcs-bucket-name/...

--- Starting Evaluation Task ---
Dataset has 2 rows.
...
--- Evaluation Complete ---
Summary Metrics:
                                           Metric  Value
0             trajectory_single_tool_use/mean_score    0.5
1                response_follows_trajectory/mean    1.0
...

```

**Analizando los resultados**

  * `trajectory_single_tool_use/mean_score: 0.5`: Esto tiene sentido. La métrica se configuró para comprobar **solo** `get_product_price`. Se utilizó en uno de nuestros dos casos de prueba, por lo que la puntuación es del 50%.
  * `response_follows_trajectory/mean: 1.0`: Esto indica que, en ambos casos, el LLM como juez determinó que la respuesta final del agente era una conclusión lógica a partir de la herramienta que utilizó.

Puedes encontrar los resultados completos, fila por fila, en el bucket de GCS que creaste y ver un panel visual en la sección de Experimentos de Vertex AI en la Google Cloud Console.

## H2 4: Limpieza

Para evitar incurrir en cargos continuos, limpia los recursos que creaste.

1.  **Eliminar el Experimento de Vertex AI:**
    
      * Navega a Experimentos de Vertex AI en la Cloud Console.
      * Selecciona el experimento llamado `adk-product-agent-evaluation` y elimínalo.

2.  **Eliminar el Bucket de GCS:** Ejecuta el siguiente comando en tu terminal:
    
    ``` console
    gsutil rm -r gs://your-unique-gcs-bucket-name
    
    ```

**¡Felicidades!**

Has evaluado con éxito un agente de Google ADK utilizando el servicio de Evaluación gestionado de Vertex AI.
