import asyncio
# Importe el agente que definió en main.py
from agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from dotenv import load_dotenv

# Cargue las variables de entorno desde el archivo .env
load_dotenv()

# Un nombre único para su aplicación.
APP_NAME = "mi_primer_app"

# IDs únicos para el usuario y la sesión de conversación.
USER_ID = "user_12345"
SESSION_ID = "session_67890"

async def main():
    """La función principal para ejecutar el agente de forma programática."""
    # 1. El Runner es el punto de entrada principal para ejecutar un agente.
    # Requiere el agente a ejecutar y un servicio de sesión para almacenar el historial.
    runner = Runner(
        agent=root_agent,
        session_service=InMemorySessionService(),
        app_name=APP_NAME
    )
    # 2. Se debe crear una sesión para mantener el historial de la conversación.
    print(f"Creando sesión: {SESSION_ID}")
    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    # 3. Prepare el mensaje del usuario en el formato ADK requerido.
    user_message = Content(parts=[Part(text="Escribe un haiku sobre APIs.")])
    print(f"Mensaje del usuario: '{user_message.parts[0].text}'")
    # 4. El método `run` ejecuta el agente y devuelve un flujo de eventos.
    print("\n--- Respuesta del Agente ---")
    final_response = ""
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_message
    ):

    # 5. Buscamos el evento "final response" para obtener la salida del agente.
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text.strip()
            print(final_response)
    print("--- Fin de la Respuesta ---\n")
# Ejecutar la función principal asíncrona.
if __name__ == "__main__":
    asyncio.run(main())