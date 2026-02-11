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
