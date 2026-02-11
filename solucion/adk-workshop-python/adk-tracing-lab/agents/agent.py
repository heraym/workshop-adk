# agent.py

from google.adk.agents import LlmAgent

def get_weather(city: str) -> dict:
    """Retrieves the current weather for a specified city."""
    print(f"Tool call: get_weather(city='{city}')")
    if city.lower() == "paris":
        return {
            "status": "success",
            "report": "The weather in Paris is cloudy with a temperature of 18°C.",
        }
    return {"status": "error", "message": f"Weather for '{city}' not found."}

root_agent = LlmAgent(
    name="weather_agent_traced",
    model="gemini-2.5-flash",
    description="An agent that can provide weather reports and is traced.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)