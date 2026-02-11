# query_agent.py

import asyncio
from vertexai import agent_engines

# TODO: Pega el Nombre del Recurso de la salida del script de implementación aquí
AGENT_RESOURCE_NAME = "projects/224237244779/locations/us-central1/reasoningEngines/7830320491276533760"

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
