# agent.py`

from google.adk.agents import Agent

def get_weather(city: str) -> dict:

  """Retrieves the current weather for a specified city."""

  print(f"Tool call: get_weather(city='{city}')")

  if city.lower() == "new york":

    return {

        "status": "success",

        "report": "The weather in New York is sunny with a temperature of 25°C.",

    }

  return {"status": "error", "message": f"Weather for '{city}' not found."}

# The 'root_agent' variable is what the ADK framework discovers.

root_agent = Agent(
  name="weather_agent",
  model="gemini-2.5-flash",
  description="An agent that can provide weather reports.",
  instruction="You must use the available tools to find an answer.",
  tools=[get_weather],
)