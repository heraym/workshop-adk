## H1 Gestionando la memoria de tu agente ADK**

En este laboratorio, aprenderás uno de los conceptos más poderosos en la creación de agentes de IA avanzados: **memoria**. Al igual que los humanos, los agentes necesitan recordar interacciones pasadas para mantener conversaciones significativas y conscientes del contexto. Mejorarás un agente básico dándole un almacenamiento en memoria a corto plazo, permitiéndole recordar información de una conversación y utilizarla en la siguiente.

Este laboratorio se centra en `InMemoryMemoryService`, la herramienta perfecta para el desarrollo local y prototipado. Verás de primera mano cómo un agente puede almacenar información y luego recuperarla más tarde para responder preguntas, haciendo que sus respuestas sean más inteligentes y relevantes.
 

## H2 1. Crear el agente

En el directorio del workshop vamos a crear un directorio mi_agente_con_memoria

Dentro de ese directorio, crea un único archivo Python llamado `memory_lab.py`, y los archivos `__init__.py` y `.env`.
Copia los archivos `__init__.py` y `.env` del laboratorio anterior.
Copia el siguiente código de inicio en `run_agent.py`. Este código define nuestros dos agentes: uno para capturar información y otro que eventualmente la recordará.


``` 
# run_agent.py (Código de inicio)

import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# 1. Definir Constantes
APP_NAME = "memory_lab_app"
USER_ID = "test_user_123"
MODEL = "gemini-2.5-flash"

# 2. Definir Agentes

# El único trabajo de este agente es tener una conversación donde el usuario proporciona una pieza de información.
info_capture_agent = Agent(
    model=MODEL,
    name="InfoCaptureAgent",
    instruction="Eres un asistente. Reconoce la declaración del usuario en un tono amigable.",
)

# Este agente eventualmente podrá recordar información de la memoria.
memory_recall_agent = Agent(
    model=MODEL,
    name="MemoryRecallAgent",
    instruction="Responde a la pregunta del usuario. Si no sabes la respuesta, dilo.",
)

# 3. Definir la lógica principal del escenario
async def run_memory_scenario():
    """Ejecuta un escenario de dos turnos para demostrar la memoria."""
    print("Iniciando escenario... (Memoria AÚN NO IMPLEMENTADA)")

    # Aquí es donde añadiremos el servicio de memoria y ejecutaremos nuestro escenario.

# 4. Ejecutar el Script
if __name__ == "__main__":
    asyncio.run(run_memory_scenario())

```

## H2 2. Implementar el InMemoryMemoryService

Ahora, añadamos memoria a nuestra aplicación. El `InMemoryMemoryService` almacena el historial de conversación en la RAM de tu computadora. Es rápido y no requiere configuración, pero recuerda: toda la memoria almacenada se pierde cuando finaliza el script.

*** Importar el servicio de memoria y la herramienta de memoria ***

Añade las siguientes importaciones en la parte superior de `run_agent.py`:

``` python
from google.adk.memory import InMemoryMemoryService # Importar el servicio de memoria
from google.adk.tools import load_memory          # Importar la herramienta incorporada para buscar en la memoria

```

***  Equipar al `memory_recall_agent` con la herramienta `load_memory` ***

Para que un agente pueda buscar en la memoria, necesita la herramienta adecuada. Actualiza la definición de `memory_recall_agent` para incluir la herramienta `load_memory` y ajusta sus instrucciones para fomentar su uso.

``` python
# run_agent.py

# ... (código anterior) ...

# Este agente eventualmente podrá recordar información de la memoria.
memory_recall_agent = LlmAgent(
    model=MODEL,
    name="MemoryRecallAgent",
    instruction="Responde a la pregunta del usuario. Usa la herramienta 'load_memory' "
                "si la respuesta puede estar en conversaciones pasadas.",
    tools=[load_memory] # <-- AÑADE ESTA LÍNEA
)

# ... (resto del código) ...

```

***  Instanciar los Servicios ***

Dentro de la función `run_memory_scenario`, necesitamos crear instancias de nuestros servicios. Crearemos un único `InMemorySessionService` y un único `InMemoryMemoryService` para que sean compartidos a través de ambos turnos conversacionales. Esta es la clave para compartir el contexto.

Actualiza la función `run_memory_scenario` de esta manera:

``` python
# run_agent.py

# ... (código anterior) ...

async def run_memory_scenario():
    """Ejecuta un escenario de dos turnos para demostrar la memoria."""
    print("🚀 Iniciando escenario con InMemoryMemoryService!")

    # Instanciar los servicios que serán compartidos.
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    # El resto de nuestra lógica irá aquí.

```

Ahora nuestra aplicación está configurada para usar memoria. En el siguiente paso, implementaremos la lógica para almacenarla y recuperarla.

**El flujo de trabajo de "Memoria": Almacenamiento y Recuperación**

El flujo de trabajo central para usar memoria en ADK implica dos pasos distintos:

Ingesta: Después de que se completa una conversación, añades explícitamente su objeto `Session` al `MemoryService`.
Recuperación: En una conversación futura, un agente equipado con la herramienta `load_memory` puede buscar en ese `MemoryService` información relevante.

Implementemos este flujo.

*** Parte 1: La Primera Conversación (Almacenar Información) ***

Añade el siguiente código dentro de `run_memory_scenario`, justo después de instanciar los servicios. Este bloque de código ejecutará nuestro `info_capture_agent`, obtendrá el color favorito del usuario y luego guardará toda esa conversación en nuestro `memory_service`.

``` python
# memory_lab.py -> dentro de run_memory_scenario()

    # TURNO 1: CAPTURAR Y ALMACENAR INFORMACIÓN
    print("\n--- Turno 1: Capturando Información ---")
    runner1 = Runner(
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service # Proporcionar el servicio de memoria al Runner
    )
    session1_id = "session_for_storing"
    await runner1.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session1_id
    )
    user_input1 = Content(parts=[Part(text="Mi color favorito es el azul.")], role="user")

    print(f"👤 Entrada del usuario: {user_input1.parts[0].text}")

    # Ejecutar el agente e imprimir su respuesta
    async for event in runner1.run_async(
        user_id=USER_ID, session_id=session1_id, new_message=user_input1
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"🤖 Respuesta del Agente 1: {event.content.parts[0].text}")

    # PASO CRÍTICO: Añadir la sesión completada al servicio de memoria
    print("\n--- Añadiendo Sesión 1 a la Memoria ---")
    completed_session1 = await runner1.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session1_id
    )
    await memory_service.add_session_to_memory(completed_session1)
    print("✅ Sesión añadida a la memoria.")

```

*** Parte 2: La Segunda Conversación (Recuperar Información) ***

Ahora, añade el bloque final de código a `run_memory_scenario`. Esta parte simula una conversación completamente nueva. Usaremos nuestro `memory_recall_agent` y le preguntaremos sobre nuestro color favorito. Debido a que su `Runner` está conectado al *mismo* `memory_service`, la herramienta `load_memory` encontrará el contexto del Turno 1.

``` python
# run_agent.py -> dentro de run_memory_scenario()

    # TURNO 2: RECUPERAR INFORMACIÓN EN UNA SESIÓN NUEVA
    print("\n--- Turno 2: Recuperando Información ---")
    runner2 = Runner(
        agent=memory_recall_agent, # Usar el segundo agente
        app_name=APP_NAME,
        session_service=session_service, # Reutilizar los mismos servicios
        memory_service=memory_service
    )
    session2_id = "session_for_recalling"
    await runner2.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session2_id
    )
    user_input2 = Content(parts=[Part(text="¿Cuál es mi color favorito?")], role="user")

    print(f"👤 Entrada del usuario: {user_input2.parts[0].text}")

    # Ejecutar el segundo agente e imprimir su respuesta
    async for event in runner2.run_async(
        user_id=USER_ID, session_id=session2_id, new_message=user_input2
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"🤖 Respuesta del Agente 2: {event.content.parts[0].text}")

```

*** Ejecutar y Observar ***

Tu archivo `run_agent.py` debería estar completo ahora. ¡Es hora de ejecutarlo y ver la memoria en acción\!

*** Código Final ***

Para tu referencia, aquí está el código completo para `run_agent.py`:

``` python
# run_agent.py (Código Final)

import asyncio
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory
from google.genai.types import Content, Part
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# 1. Definir Constantes
APP_NAME = "memory_lab_app"
USER_ID = "test_user_123"
MODEL = "gemini-1.5-flash"

# 2. Definir Agentes
info_capture_agent = LlmAgent(
    model=MODEL,
    name="InfoCaptureAgent",
    instruction="Eres un asistente. Reconoce la declaración del usuario en un tono amigable.",
)

memory_recall_agent = LlmAgent(
    model=MODEL,
    name="MemoryRecallAgent",
    instruction="Responde a la pregunta del usuario. Usa la herramienta 'load_memory' "
                "si la respuesta puede estar en conversaciones pasadas.",
    tools=[load_memory]
)

# 3. Definir la lógica principal del escenario
async def run_memory_scenario():
    """Ejecuta un escenario de dos turnos para demostrar la memoria."""
    print("🚀 Iniciando escenario con InMemoryMemoryService!")

    # Instanciar los servicios que serán compartidos.
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    # TURNO 1: CAPTURAR Y ALMACENAR INFORMACIÓN
    print("\n--- Turno 1: Capturando Información ---")
    runner1 = Runner(
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service
    )
    session1_id = "session_for_storing"
    await runner1.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session1_id
    )
    user_input1 = Content(parts=[Part(text="Mi color favorito es el azul.")], role="user")

    print(f"👤 Entrada del usuario: {user_input1.parts[0].text}")

    async for event in runner1.run_async(
        user_id=USER_ID, session_id=session1_id, new_message=user_input1
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"🤖 Respuesta del Agente 1: {event.content.parts[0].text}")

    print("\n--- Añadiendo Sesión 1 a la Memoria ---")
    completed_session1 = await runner1.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session1_id
    )
    await memory_service.add_session_to_memory(completed_session1)
    print("✅ Sesión añadida a la memoria.")

    # TURNO 2: RECUPERAR INFORMACIÓN EN UNA SESIÓN NUEVA
    print("\n--- Turno 2: Recuperando Información ---")
    runner2 = Runner(
        agent=memory_recall_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service
    )
    session2_id = "session_for_recalling"
    await runner2.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session2_id
    )
    user_input2 = Content(parts=[Part(text="¿Cuál es mi color favorito?")], role="user")

    print(f"👤 Entrada del usuario: {user_input2.parts[0].text}")

    async for event in runner2.run_async(
        user_id=USER_ID, session_id=session2_id, new_message=user_input2
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"🤖 Respuesta del Agente 2: {event.content.parts[0].text}")

# --- 4. Ejecutar el Script ---
if __name__ == "__main__":
    # NOTA: Es posible que necesites configurar tu variable de entorno GOOGLE_API_KEY.
    asyncio.run(run_memory_scenario())

```

*** Ejecutar el Script ***

Abre tu terminal, navega al directorio `mi_agente_con_memoria` y ejecuta el archivo:

``` console
python run_agent.py

```

**Salida Esperada**

Deberías ver una salida similar a la siguiente. La clave es que el Agente 2 identifica correctamente el color favorito sin que se le diga en la segunda conversación.

``` console
🚀 Iniciando escenario con InMemoryMemoryService!

--- Turno 1: Capturando Información ---
🤖 Respuesta del Agente 1: ¡Es una gran elección! El azul es un color muy relajante.

--- Añadiendo Sesión 1 a la Memoria ---
✅ Sesión añadida a la memoria.

--- Turno 2: Recuperando Información ---
🤖 Respuesta del Agente 2: Tu color favorito es el azul.

```

*** Memoria vs. Artefactos: Un Puente Conceptual ***

Has utilizado con éxito la Memoria. ¿Pero qué pasa con los agentes multimodales? ¿Y si el usuario hubiera enviado una imagen en lugar de texto? Aquí es donde otro concepto de ADK, los Artefactos, se vuelve importante.

*** Memoria vs. Artefactos ***
 
La memoria (`MemoryService`) sirve para almacenar y buscar "contexto conversacional". Piensa en ella como un registro buscable de las cosas que se dijeron. La información es principalmente textual y la utiliza el LLM para comprender la historia.

Los artefactos (`ArtifactService`) sirven para almacenar y recuperar "datos binarios" con nombre y versión. Piensa en ellos como archivos: imágenes, PDF, clips de audio, etc. La herramienta `load_memory` no puede buscarlos directamente, pero otras herramientas pueden cargarlos por nombre de archivo para procesarlos.

*** ¡Felicitaciones\! ***

¡Has implementado con éxito un componente central de los agentes inteligentes: la memoria\!

 
