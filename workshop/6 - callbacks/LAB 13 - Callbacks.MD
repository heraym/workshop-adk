## H1  Usando Callbacks de Tools

En este lab, vamos a ver como usar el concepto de callback para validar y re-formatear el input para una tool.
Tenemos un ejemplo de un agente que usa una tool para devolver el estado del clima de una ciudad en un pais.
Vamos a usar un callback para controlar el nombre del pais y en caso de recibir una abreviatura, formatearla a nombre de pais.

## H2 1. Configura tu entorno
Primero, preparemos tu entorno de desarrollo local. Crearemos una carpeta de proyecto dedicada, configuraremos un entorno virtual de Python para mantener nuestras dependencias aisladas e instalaremos el ADK.

Usaremos un solo comando de ADK para generar la estructura de un proyecto de agente completo basado en código.
Desde tu directorio adk-workshop-python (con el entorno virtual aún activo), ejecuta el siguiente comando:

`adk create --type=code adk_mi_callback_tool`

Cuando solicita el modelo elijamos gemini-2.5-flash:

```Choose a model for the root agent:
1. gemini-2.5-flash
2. Other models (fill later)
Choose model (1, 2): 1 ```

Elijamos Vertex AI como backend
```1. Google AI
2. Vertex AI
Choose a backend (1, 2): 2


You need an existing Google Cloud account and project, check out this link for details:
https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai 
```

Elije proyecto y region:

```Enter Google Cloud project ID [xxxx-xxxxx-xxxxxxxx]: 
Enter Google Cloud region [us-central1]: 
```
## H2 2. Configura tu agente
Edita agent.py para crear el agente:

```
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Optional, Dict, Any
from google.adk.tools import FunctionTool
from google.adk.agents.llm_agent import LlmAgent
import httpx, requests
import json


COUNTRY_ABBREV_DICT = {
    "USA": "United States",
    "UK": "United Kingdom",
    "GB": "United Kingdom",
    "UAE": "United Arab Emirates",
    "DRC": "DR Congo",
    "CAR": "Central African Republic"
}

#-------------------
# tools
#-------------------
async def find_current_weather(latitude: float, longitude: float) -> float:
    """Find weather given geographical location
    Args:
        latitude: A float representing the latitude of a geographical location.
        longitude: A float representing the longitude of a geographical location.

    Returns:
        float: Current temperature in Celsius
    """
    verify=True
    url = "https://api.open-meteo.com/v1/forecast"

    query=f"{url}?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    try:
        response = requests.get(query, verify=verify)
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    json_data = json.loads(response.text)

    return json_data["current"]["temperature_2m"]

async def get_geocoding(city: str, country: str) -> dict:
    """Find geographical location given city and country
    Args:
        city: A string representing the name of the city.
        country: A string representing the name or country code of the country.

    Returns:
        dict: Latitude and longitude of the city, country.
    """
    verify=True

    url = "https://geocoding-api.open-meteo.com/v1/search"
  
    query=f"{url}?name={city}"
    try:
        response = requests.get(query, verify=verify)
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    json_data = json.loads(response.text)

    try:
        for entry in json_data["results"]:
            try:
                if entry["country"].lower() == country.lower():
                    return {"latitude": entry["latitude"], "longitude": entry["longitude"]}
            except KeyError:
                return None
    except KeyError:
        return None


current_weather_tool = FunctionTool(func=find_current_weather)
geocoding_tool = FunctionTool(func=get_geocoding)

#-------------------
# callbacks
#-------------------

def country_name_before_tool_modifier(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Original args: {args}")

    if tool_name == 'get_geocoding' and args.get('country', '').upper() in COUNTRY_ABBREV_DICT:
        print(f"[Callback] Detected {args.get('country', '').upper()}. Modifying arg to {COUNTRY_ABBREV_DICT[args.get('country', '').upper()]}.")
        args['country'] = COUNTRY_ABBREV_DICT[args.get('country', '').upper()]
        print(f"[Callback] Modified args: {args}")
        return None

    return None


#-----------------
# agents
#-----------------
root_agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions about the weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the weather in a city and country."
    ),
    tools=[
        geocoding_tool,
        current_weather_tool
    ],
    before_tool_callback=country_name_before_tool_modifier,
)
```

## H2 3. Pruebalo
Si lo pruebas por ejemplo pidiendo "Dime el clima en Londres, GB" vas a ver que ejecuta el callback y transforma "GB" por "Gran Bretaña".

