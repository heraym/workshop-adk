# H1  Construcción de Agentes Potenciados por API con Herramientas OpenAPI

 Has aprendido a trabajar con diferentes modelos y a combinar varios tipos de herramientas. Ahora, descubrirás cómo generar herramientas automáticamente a partir de especificaciones OpenAPI, permitiendo que tus agentes interactúen con cualquier API REST que siga el estándar OpenAPI.

OpenAPI (anteriormente Swagger) es el estándar de la industria para describir APIs REST. El conjunto de herramientas OpenAPI de ADK puede analizar automáticamente estas especificaciones y generar herramientas de función para tu agente, convirtiendo cualquier API bien documentada en una capacidad instantánea para el agente. Esto significa que puedes integrarte con miles de APIs existentes sin escribir código de integración personalizado.

## H2 - 1. Configura tu laboratorio OpenAPI

Creemos un entorno dedicado para experimentar con las herramientas OpenAPI y las integraciones de API externas.
Abre tu terminal y accede al directorio del workshop

Crea la estructura del proyecto:
`adk create --type=code petstore_agent`
  

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

## H2 3. Crea tu agente de Pet Store API
Construyamos un agente que pueda administrar una tienda de mascotas usando una API simulada. Usaremos httpbin.org, que proporciona endpoints de prueba que devuelven nuestras solicitudes.

Crear la implementación del agente

Modifica petstore_agent/agent.py con el siguiente código:

```
import asyncio
import uuid  # For unique session IDs
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- OpenAPI Tool Imports ---
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

# --- Load Environment Variables ---
load_dotenv()

# --- Constants ---
AGENT_NAME_OPENAPI = "petstore_manager_agent"
GEMINI_MODEL = "gemini-2.0-flash"

# --- Sample OpenAPI Specification (JSON String) ---
# A basic Pet Store API example using httpbin.org as a mock server
openapi_spec_string = """
{
  "openapi": "3.0.0",
  "info": {
    "title": "Simple Pet Store API (Mock)",
    "version": "1.0.1",
    "description": "An API to manage pets in a store, using httpbin for responses."
  },
  "servers": [
    {
      "url": "https://httpbin.org",
      "description": "Mock server (httpbin.org)"
    }
  ],
  "paths": {
    "/get": {
      "get": {
        "summary": "List all pets (Simulated)",
        "operationId": "listPets",
        "description": "Simulates returning a list of pets. Uses httpbin's /get endpoint which echoes query parameters.",
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "description": "Maximum number of pets to return",
            "required": false,
            "schema": { "type": "integer", "format": "int32" }
          },
          {
             "name": "status",
             "in": "query",
             "description": "Filter pets by status",
             "required": false,
             "schema": { "type": "string", "enum": ["available", "pending", "sold"] }
          }
        ],
        "responses": {
          "200": {
            "description": "A list of pets (echoed query params).",
            "content": { "application/json": { "schema": { "type": "object" } } }
          }
        }
      }
    },
    "/post": {
      "post": {
        "summary": "Create a pet (Simulated)",
        "operationId": "createPet",
        "description": "Simulates adding a new pet. Uses httpbin's /post endpoint which echoes the request body.",
        "requestBody": {
          "description": "Pet object to add",
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                  "name": {"type": "string", "description": "Name of the pet"},
                  "tag": {"type": "string", "description": "Optional tag for the pet"}
                }
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Pet created successfully (echoed request body).",
            "content": { "application/json": { "schema": { "type": "object" } } }
          }
        }
      }
    },
    "/get?petId={petId}": {
      "get": {
        "summary": "Info for a specific pet (Simulated)",
        "operationId": "showPetById",
        "description": "Simulates returning info for a pet ID. Uses httpbin's /get endpoint.",
        "parameters": [
          {
            "name": "petId",
            "in": "path",
            "description": "This is actually passed as a query param to httpbin /get",
            "required": true,
            "schema": { "type": "integer", "format": "int64" }
          }
        ],
        "responses": {
          "200": {
            "description": "Information about the pet (echoed query params)",
            "content": { "application/json": { "schema": { "type": "object" } } }
          },
          "404": { "description": "Pet not found (simulated)" }
        }
      }
    }
  }
}
"""

# --- Create OpenAPIToolset ---
petstore_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='json',
    # No authentication needed for httpbin.org
    # Optional: tool_filter=['createPet', 'showPetById'] to limit available tools
)

# --- Agent Definition ---
root_agent = LlmAgent(
    name=AGENT_NAME_OPENAPI,
    model=GEMINI_MODEL,
    tools=[petstore_toolset],
    instruction="""You are a Pet Store assistant managing pets via an API.
    Use the available tools to fulfill user requests.

    Available operations:
    - listPets: Get a list of all pets (with optional filters)
    - createPet: Add a new pet to the store
    - showPetById: Get information about a specific pet

    When creating a pet, confirm the details echoed back by the API.
    When listing pets, mention any filters used (like limit or status).
    When showing a pet by ID, state the ID you requested.
    Always be helpful and explain what actions you're taking.
    """,
    description="Manages a Pet Store using tools generated from an OpenAPI spec."
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

## H2 5. Comprendiendo la generación de herramientas

Cuando ADK procesa esta especificación, crea:
listPets(): función del endpoint GET /get
createPet(): función del endpoint POST /post
showPetById(): función del endpoint GET /get?petId={petId}
Cada función incluye sugerencias de tipo adecuadas, documentación y manejo de errores.

## H2 6. Prueba tu agente potenciado por OpenAPI

¡Veamos tus herramientas de API generadas automáticamente en acción!

Iniciar el agente
Desde el directorio raíz de tu proyecto, inicia la interfaz web de ADK:

`adk web`
Abre tu navegador en http://127.0.0.1:8080 y prueba con estos prompts:
Listar todas las mascotas en la tienda
Muéstrame mascotas con estado disponible y limita a 5 resultados
Crear una nueva mascota llamada Buddy con la etiqueta amigable
Muéstrame información sobre la mascota con ID 123
Entendiendo las respuestas

Dado que estamos usando httpbin.org como servidor simulado, verás respuestas como:
{
  "args": {"limit": "5", "status": "available"},
  "headers": {...},
  "url": "https://httpbin.org/get?limit=5&amp;status=available"
}

Esto demuestra que:
Los parámetros se pasan correctamente a la API
Las solicitudes HTTP están formateadas adecuadamente
El agente puede interpretar y explicar las respuestas

## H2 7. Funciones avanzadas de OpenAPI

```
# Agregar autenticación
Para APIs reales que requieren autenticación, puedes agregar esquemas de autenticación:
from google.adk.tools.openapi_tool.auth_schemes import APIKey
from google.adk.tools.openapi_tool.auth_credentials import AuthCredential


# Ejemplo: Autenticación por clave de API
auth_scheme = APIKey(name="X-API-Key", location="header")
auth_credential = AuthCredential(
    auth_type="API_KEY",
    value="your-api-key-here"
)


petstore_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='json',
    auth_scheme=auth_scheme,
    auth_credential=auth_credential
)

```

Filtrado de herramientas disponibles
Puedes limitar qué herramientas se generan:

petstore_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='json',
    tool_filter=['createPet', 'listPets']  # Solo generar estas herramientas
)

Carga desde archivos externos
Para proyectos reales, carga las especificaciones desde archivos:

```
# Cargar desde archivo local
with open('petstore-api.json', 'r') as f:
    spec_content = f.read()


# O cargar desde URL
import requests
response = requests.get('https://api.example.com/openapi.json')
spec_content = response.text


petstore_toolset = OpenAPIToolset(
    spec_str=spec_content,
    spec_str_type='json'
)
```

## H2 8. Patrones de integración en el mundo real

*** Manejo de errores y validación ***

```
instruction="""Eres un asistente de Pet Store que gestiona mascotas a través de una API.


Pautas de manejo de errores:
- Si una llamada a la API falla, explica el error claramente al usuario
- Para errores de validación, guía al usuario sobre el formato de entrada correcto
- Si no se encuentra una mascota, sugiere acciones alternativas
- Siempre reintenta las solicitudes fallidas una vez antes de desistir


Cuando las APIs devuelven errores, interprétalos de manera útil para el usuario.
"""

```

***Interpretación de respuestas***
```
instruction="""Eres un asistente de Pet Store que gestiona mascotas a través de una API.


Interpretación de respuestas:
- Al listar mascotas, resume la información clave claramente
- Para operaciones de creación, confirma el éxito y proporciona los siguientes pasos
- Al mostrar detalles de una mascota, destaca la información más importante
- Siempre explica qué significa la respuesta de la API en lenguaje sencillo


Transforma las respuestas técnicas de la API en información amigable para el usuario.
"""
```

## H2 9. ¡Felicitaciones!
¡Has construido con éxito un agente impulsado por herramientas OpenAPI generadas automáticamente!
