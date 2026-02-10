# H1  Construcción de Agentes Potenciados por API con Herramientas OpenAPI

 Has aprendido a trabajar con diferentes modelos y a combinar varios tipos de herramientas. Ahora, descubrirás cómo generar herramientas automáticamente a partir de especificaciones OpenAPI, permitiendo que tus agentes interactúen con cualquier API REST que siga el estándar OpenAPI.

OpenAPI (anteriormente Swagger) es el estándar de la industria para describir APIs REST. El conjunto de herramientas OpenAPI de ADK puede analizar automáticamente estas especificaciones y generar herramientas de función para tu agente, convirtiendo cualquier API bien documentada en una capacidad instantánea para el agente. Esto significa que puedes integrarte con miles de APIs existentes sin escribir código de integración personalizado.

## H2 - 1. Configura tu laboratorio OpenAPI

Creemos un entorno dedicado para experimentar con las herramientas OpenAPI y las integraciones de API externas.
Abre tu terminal y accede al directorio del workshop

Crea la estructura del proyecto:
`adk create --type=code mi_agente_openapi_weather`
  

## H2 - 2. Entendiendo OpenAPI y la generación de herramientas

Antes de construir nuestro agente, entendamos qué hace que los conjuntos de herramientas OpenAPI sean tan poderosos:

¿Qué es OpenAPI?

OpenAPI es una especificación para describir APIs REST. Define:
Endpoints: Qué URLs y métodos HTTP están disponibles.
Parámetros: Qué entradas espera cada endpoint.
Respuestas: Qué estructura de datos devuelve cada endpoint.
Autenticación: Cómo autenticarse con la API.
Modelos de datos: La estructura de los objetos de solicitud y respuesta.

Cómo ADK genera herramientas

El OpenAPIToolset de ADK realiza la siguiente magia:
*** Analiza la especificación OpenAPI (JSON o YAML).
Genera herramientas individuales para cada endpoint de la API.
Crea firmas de función adecuadas con sugerencias de tipo.
Maneja solicitudes HTTP, autenticación y gestión de errores.
Devuelve respuestas estructuradas que tu agente puede entender. ***

¡Esto significa que una sola especificación OpenAPI puede darle instantáneamente a tu agente docenas de capacidades!

## H2 3. Crea tu agente de OpenAPI Weather  API
Construyamos un agente que pueda darnos informacion de clima usando la API de openweathermap.org.  

Crear la implementación del agente

Modifica mi_agente_openapi_weather/agent.py con el siguiente código:

```
import asyncio
import uuid  # For unique session IDs
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- OpenAPI Tool Imports ---
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
      "url": "https://api.openweathermap.org/data/3.0",
      "description": "Open Weather API"
    }
  ],
  "paths": {
    "/onecall": {
      "get": {
        "summary": "Get Current Conditions",
        "operationId": "currentConditions",
        "description": "Get access to current weather, minute forecast for 1 hour, hourly forecast for 48 hours, daily forecast for 8 days and government weather alerts.",
        "parameters": [
          ? lon={lon}&exclude={part}&appid={API key}"
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
    Use the following value <your_api_key> for appid.

    Available operations:
    - currentConditions:  Get access to current weather, minute forecast for 1 hour, hourly forecast for 48 hours, daily forecast for 8 days and government weather alerts.
    """,
    description="Provides weather info from an OpenAPI spec."
)

```

## H2 4. Comprendiendo la especificación OpenAPI

Analicemos los componentes clave de nuestra especificación OpenAPI:

info: Metadatos sobre la API
servers: URLs base donde se aloja la API
paths: Endpoints disponibles y sus operaciones
operationId: Identificadores únicos que se convierten en nombres de funciones de herramientas
parameters: Parámetros de entrada para cada endpoint
requestBody: Estructura para los cuerpos de solicitud POST/PUT
responses: Formatos de respuesta esperados

 

## H2 5. Prueba tu agente potenciado por OpenAPI

¡Veamos tus herramientas de API generadas automáticamente en acción!

Iniciar el agente
Desde el directorio raíz de tu proyecto, inicia la interfaz web de ADK:

`adk web`
Abre tu navegador en http://127.0.0.1:8080 y prueba con estos prompts:
Como esta el clima en la latitud -34.609032, longitud -58.381557


## H2 7. Funciones avanzadas de OpenAPI

*** Autenticacion ***
Para el caso que se necesite autenticacion revisar https://google.github.io/adk-docs/tools-custom/authentication/#api-key

*** Filtrado de herramientas disponibles ***
Puedes limitar qué herramientas se generan:

petstore_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='json',
    tool_filter=['operacion1', 'operacion2']  # Solo generar estas herramientas
)

*** Carga desde archivos externos ***
Para proyectos reales, carga las especificaciones desde archivos:

```
# Cargar desde archivo local
with open('ejemplo-api.json', 'r') as f:
    spec_content = f.read()


# O cargar desde URL
import requests
response = requests.get('https://api.example.com/openapi.json')
spec_content = response.text


ejemplo_toolset = OpenAPIToolset(
    spec_str=spec_content,
    spec_str_type='json'
)
```

## H2 8. Patrones de integración en el mundo real

*** Manejo de errores y validación ***

```
instruction="""Eres un asistente que da informacion del clima a través de una API.


Pautas de manejo de errores:
- Si una llamada a la API falla, explica el error claramente al usuario
- Para errores de validación, guía al usuario sobre el formato de entrada correcto
- Si no se encuentra un lugar, sugiere acciones alternativas
- Siempre reintenta las solicitudes fallidas una vez antes de desistir


Cuando las APIs devuelven errores, interprétalos de manera útil para el usuario.
"""


## H2 9. ¡Felicitaciones!
¡Has construido con éxito un agente impulsado por herramientas OpenAPI generadas automáticamente!
