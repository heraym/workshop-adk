# compras_agent/test.py
import asyncio
from agent import root_agent, remote_info_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

async def test():
    # Inicializar el servicio de sesión local en memoria
    session_service = InMemorySessionService()
    
    # Crear una sesión de prueba
    session_id = "test-session-compras"
    user_id = "test-user-123"
    await session_service.create_session(app_name=root_agent.name, session_id=session_id, user_id=user_id)

    # Configurar el Runner local para ejecutar el agente orquestador compras_agent
    runner = Runner(
        app_name=root_agent.name,
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=session_service,
        memory_service=InMemoryMemoryService(),
    )

    print("--- Probando compras_agent con sub-agente A2A remoto ---")
    
    # Crear un mensaje de prueba que requiere consultar al agente de información remoto
    query = "Hola, me gustaría comprar 3 unidades de producto1. ¿Me podrías decir qué es y cuál es su precio?"
    content = types.Content(role="user", parts=[types.Part.from_text(text=query)])

    print(f"Usuario: {query}\n")
    print("Iniciando ejecución...")

    # Ejecutar de forma asíncrona y emitir los eventos de respuesta
    async for event in runner.run_async(
        session_id=session_id,
        user_id=user_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            # Mostrar la respuesta intermedia o final
            for part in event.content.parts:
                if part.text:
                    print(f"Agente: {part.text}")
        elif event.error_message:
            print(f"Error: {event.error_message}")

    # Limpiar los recursos del agente remoto
    await remote_info_agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test())
