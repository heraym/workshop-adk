## H1  Construyendo un Sistema Multi-Agente con A2A en ADK

Ahora, aprenderás cómo hacer que tus agentes ADK hablen directamente entre sí.
El protocolo Agent-to-Agent (A2A) es un estándar abierto que permite esta comunicación. Te permite construir sistemas compuestos por múltiples agentes especializados que pueden delegar tareas y colaborar. Piensa en ello como construir un equipo de expertos: un agente podría orquestar tareas, otro podría ser experto en cálculos y un tercero podría especializarse en la recuperación de datos.
In este laboratorio, construirás un sistema completo de dos agentes desde cero:
Un Agente Especialista (math_agent) que es experto en realizar sumas. Expondremos este agente como un servicio de red.
Un Agente Orquestador que sabe cómo delegar problemas matemáticos al especialista. Enseñaremos a este agente a consumir el math_agent.

## H2 1. Configura tu entorno
Primero, preparemos tu entorno de desarrollo local. Crearemos una carpeta de proyecto dedicada, configuraremos un entorno virtual de Python para mantener nuestras dependencias aisladas e instalaremos el ADK.

Primero instalaremos las librerias:
```
pip install google-adk[a2a]
```

Usaremos un solo comando de ADK para generar la estructura de un proyecto de agente completo basado en código.
Desde tu directorio adk-workshop-python (con el entorno virtual aún activo), creemos un directorio mis_agentes_a2a.


## H2 2. Configura tus agentes
 
Organicemos nuestro código. Crearemos archivos separados para cada agente dentro de nuestro directorio actual.
Crea los dos nuevos archivos vacíos:


```console
mkdir mis_agentes_a2a
touch .env
touch mis_agentes_a2a/__init__.py
touch mis_agentes_a2a/math_agent.py
touch mis_agentes_a2a/agent.py
```

IMPORTANTE: No olvides activar venv en todas las terminales.

## H2 3. Crear y Exponer el Agente Matemático Especialista

Nuestra primera tarea es construir el math_agent. Este agente tendrá una habilidad simple: sumar dos números. Luego expondremos esta habilidad al mundo (o al menos a nuestra red local) usando las utilidades A2A de ADK.

Abre el archivo mis_agentes_a2a/math_agent.py y añade el siguiente código:
```
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv


# Cargar variables de entorno desde el archivo .env
load_dotenv()


# Definir la Habilidad Principal del Agente
def add(a: int, b: int) -> int:
    """Suma dos números enteros."""
    print(f"[math_agent] Ejecutando add({a}, {b})")
    return a + b


# Definir el Agente ADK
math_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='math_agent',
    instruction="Eres un experto en matemáticas. Usas la herramienta 'add' para realizar sumas.",
    tools=[
        FunctionTool(add)
    ],
)


# Exponer el Agente vía A2A
# La función to_a2a() envuelve nuestro agente en una aplicación de servidor web (FastAPI)
# que habla el protocolo A2A. También genera automáticamente la
# tarjeta de agente requerida para que otros agentes sepan cómo hablar con él.

a2a_app = to_a2a(math_agent, port=8001)
```


## H2 4. Crear y Configurar el Agente Orquestador

Ahora construimos el agent. Su trabajo no es hacer matemáticas por sí mismo, sino reconocer cuándo se necesitan y delegar la tarea al math_agent. Lo hará "consumiendo" el servicio A2A que acabamos de crear.

Abre el archivo agents/agent.py y añade el siguiente código:
```
# agents/agent.py
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv


# Cargar variables de entorno desde el archivo .env
load_dotenv()


# Configurar el Cliente del Agente Remoto
# RemoteA2aAgent es el componente del lado del cliente que sabe cómo hablar con
# un servidor A2A. Lo configuramos con la URL de nuestro math_agent.
math_service = RemoteA2aAgent(
    name="math_service",
    description="Un servicio que puede realizar cálculos matemáticos como sumas.",
    agent_card=(
        f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)


# Definir el Agente Orquestador
root_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='orchestrator_agent',
    instruction="""
    Eres un orquestador. Resuelves problemas delegando tareas a
    servicios especializados.
    Si el usuario pide una adición o una suma, DEBES usar el 'math_service'.
    No realices la suma tú mismo.
    """,
    # El agente remoto se trata igual que un sub-agente
    sub_agents=[
        math_service
    ],
)
```


## H2 5. Ejecutar el Sistema Multi-Agente

Este es el paso final donde todo se une. Para ejecutar nuestro sistema, necesitamos dos procesos separados ejecutándose en dos terminales distintas.

Acción Requerida: Debes usar dos ventanas de terminal para este paso. Una para el servidor A2A (el especialista) y otra para la interfaz adk web (el orquestador).

Terminal 1: Ejecutar el Servidor del math_agent Especialista
Abre tu primera terminal y asegúrate de estar en la raíz del proyecto.
Activa tu entorno virtual: source .venv/bin/activate.
Ejecuta el servidor A2A del math_agent usando uvicorn, un servidor web estándar de Python.


````console
uvicorn mis_agentes_a2a.math_agent:a2a_app --host localhost --port 8001
```

Este comando le dice a uvicorn que ejecute el objeto a2a_app que se encuentra dentro del archivo agents/math_agent.py. Deberías ver una salida que indica que el servidor se está ejecutando en http://127.0.0.1:8001. Mantén esta terminal funcionando.

Terminal 2: Ejecutar la Interfaz del Agente Orquestador
Abre tu segunda terminal. Navega a la raíz del proyecto adk-mcp-lab.
Activa tu entorno virtual: source .venv/bin/activate.
Ejecuta la interfaz adk web como de costumbre. Recogerá automáticamente nuestro nuevo agent.

adk web
Interactuar con el Sistema
Abre tu navegador en http://127.0.0.1:8000.

Selecciona agent en el menú desplegable de agentes.

Ahora, dale un problema matemático:
¿Cuánto es 123 más 456?
¡Observa la Magia!

En tu navegador, el orchestrator_agent responderá con la respuesta correcta: 579.

Ahora, mira la Terminal 1 (el servidor uvicorn). Verás el mensaje de registro que añadimos: [math_agent] Executing add(123, 456).
Esto confirma todo el flujo de trabajo:
Hablaste con el orchestrator_agent.
Entendió que necesitaba hacer una suma y delegó la tarea a su sub-agente math_service.
El RemoteA2aAgent (actuando como cliente) realizó una llamada de red al servidor math_agent que se ejecuta en el puerto 8001.
El servidor math_agent recibió la solicitud, ejecutó su herramienta add y devolvió el resultado.
El orchestrator_agent recibió el resultado y te lo presentó.

*** ¡Felicitaciones! ***
¡Has construido y orquestado con éxito un sistema multi-agente completo usando el protocolo Agent-to-Agent en ADK! Este es un paradigma poderoso que desbloquea la capacidad de construir aplicaciones de IA complejas, mantenibles y altamente especializadas.



