import asyncio
import uuid  # For unique session IDs
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- OpenAPI Tool Imports ---
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset


# --- Load Environment Variables ---
load_dotenv()

# --- Constants ---
AGENT_NAME_OPENAPI = "weather_manager_agent"
GEMINI_MODEL = "gemini-2.5-flash"

# --- Sample OpenAPI Specification (JSON String) ---
# A basic Weather Open API example using httpbin.org as a mock server
openapi_spec_string = """
{
  "openapi": "3.0.0",
  "info": {
    "title": "Open API Weather(Mock)",
    "version": "1.0.1",
    "description": "An API to manage pets in a store, using httpbin for responses."
  },
  "servers": [
    {
      "url": "https://api.openweathermap.org/data/2.5",
      "description": "Open Weather API"
    }
  ],
  "paths": {
    "/weather": {
      "get": {
        "summary": "Get Current Conditions",
        "operationId": "currentConditions",
        "description": "Get access to current weather, minute forecast for 1 hour, hourly forecast for 48 hours, daily forecast for 8 days and government weather alerts.",
        "parameters": [
          {
            "name": "lat",
            "in": "query",
            "description": "Latitude",
            "required": true,
            "schema": { "type": "decimal" }
          },
          {
            "name": "lon",
            "in": "query",
            "description": "Longitude",
            "required": true,
            "schema": { "type": "decimal" }
          },
          {
             "name": "exclude",
             "in": "query",
             "description": "By using this parameter you can exclude some parts of the weather data from the API response. It should be a comma-delimited list (without spaces). Available values: current, minutely, hourly, daily, alerts",
             "required": false,
             "schema": { "type": "string", "enum": ["current", "minutely", "hourly", "daily", "alerts"] }
          },
          {
             "name": "appid",
             "in": "query",
             "description": "Your unique API key",
             "required": true,
             "schema": { "type": "string"}
          }
        ],
        "responses": {
          "200": {
            "description": "Information about weather",
            "content": { "application/json": { "schema": { "type": "object" } } }
          }
        }
      }
    }    
  }
}
"""
 
# --- Create OpenAPIToolset ---
weather_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='json' 
)

# --- Agent Definition ---
root_agent = Agent(
    name=AGENT_NAME_OPENAPI,
    model=GEMINI_MODEL,
    tools=[weather_toolset],
    instruction="""You are a weather assistant that gives information about weather  via an API.
    Use the available tools to fulfill user requests.
    Use the following value ac2dc01641a31d9e1e0b3165320a5105 for appid.

    Available operations:
    - currentConditions:  Get access to current weather, minute forecast for 1 hour, hourly forecast for 48 hours, daily forecast for 8 days and government weather alerts.
    """,
    description="Provides weather info from an OpenAPI spec."
)


