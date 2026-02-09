from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "ba" in query.lower() or "buenos aires" in query.lower():
        return "Hacen 30 grados y esta soleado."
    return "Hace frio y muy nublado."


root_agent = Agent(
        name="WeatherAgent",
        model="gemini-2.5-flash",
        instruction="Sos un asistente que responde sobre el clima en algunas ciudades de Argentina.",
        description="An LLM agent.",
        tools=[google_search]
) 
