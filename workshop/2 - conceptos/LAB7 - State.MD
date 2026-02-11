## H1  Manejo de Estado (State) en Agentes

 Dentro de cada Sesión (nuestro hilo de conversación), el atributo **state** actúa como el *scratchpad* (bloc de notas temporal) dedicado del agente para esa interacción específica. Mientras que `session.events` mantiene el historial completo, `session.state` es donde el agente almacena y actualiza los detalles dinámicos necesarios *durante* la conversación.

**¿Qué es session.state?[¶](https://google.github.io/adk-docs/sessions/state/#what-is-sessionstate)

Conceptualmente, `session.state` es una colección (diccionario o Mapa) que contiene pares clave-valor. Está diseñado para la información que el agente necesita recordar o rastrear para que la conversación actual sea efectiva:

  * **Personalizar la interacción:** Recordar las preferencias del usuario mencionadas anteriormente (por ejemplo, 'user\_preference\_theme': 'dark').
  * **Seguimiento del progreso de la tarea:** Mantener el control de los pasos en un proceso de varios turnos (por ejemplo, 'booking\_step': 'confirm\_payment').
  * **Acumular información:** Crear listas o resúmenes (por ejemplo, 'shopping\_cart\_items': \['book', 'pen'\]).
  * **Tomar decisiones informadas:** Almacenar indicadores (*flags*) o valores que influyan en la siguiente respuesta (por ejemplo, 'user\_is\_authenticated': True).

### Características clave del estado[¶](https://google.github.io/adk-docs/sessions/state/#key-characteristics-of-state)

  
## H2 1. Creamos el agente
En el directorio del workshop vamos a crear un agente mi_agente_con_estado

`mkdir mi_agente_con_estado`

Y vamos a crear y editar el archivo agente.py.

```
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

APP_NAME = "app_state"
USER_ID = "heraym"
SESSION_ID = 'session_007'

def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "caba" in query.lower() or "buenos aires" in query.lower():
        return "Hace 35 grados y mucho sol."
    return "Llueve y esta fresquito."

root_agent = Agent(
        name="ModelAgent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. User name: {user_name}. User email: {user_email}. User city {user_city}",
        description="An LLM agent.",
        tools=[get_weather],
        output_key='model_agent_last_output'
)

session_service = InMemorySessionService()
async def run_agent_async(query, print_events=False):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if print_events:
            print('Event: ', event)
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


async def create_session(session_id, state=None):
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id, state=state)
    return session

user_profile = {
    'user_name': 'Hernan Aymard',
    'user_email': 'haymard@google.com',
    'user_city': 'Buenos Aires'
}

async def main():
    session = await create_session(SESSION_ID, state=user_profile)
    print(f"Initial state: {session.state}")

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    await run_agent_async("Como esta el clima en mi ciudad?")
    await run_agent_async("Cual es mi nombre?")

    updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print(f"Final state: {updated_session.state}")

if __name__ == "__main__":
    asyncio.run(main())

```

Este agente, me permite setear el estado inicial de una sesion con informacion de estado.

Si yo lo pruebo, ejecutando `python agente.py` obtendre el siguiente resultado:

```
Initial state: {'user_name': 'Hernan Aymard', 'user_email': 'haymard@google.com', 'user_city': 'Mar del Plata'}
Warning: there are non-text parts in the response: ['function_call'], returning concatenated text result from text parts. Check the full candidates.content.parts accessor to get the full model response.
Agent Response:  En Mar del Plata: Llueve y esta fresquito.
Agent Response:  Tu nombre es Hernan Aymard.
Final state: {'user_name': 'Hernan Aymard', 'user_email': 'haymard@google.com', 'user_city': 'Mar del Plata', 'model_agent_last_output': 'Tu nombre es Hernan Aymard.'}
```


 