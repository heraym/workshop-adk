# H1 Construir el primer Agente en ADK

¡Bienvenido al laboratorio práctico de Agentes de IA con el Kit de Desarrollo de Agentes (ADK) de Google! En esta sesión, pasarás de cero a un agente de IA totalmente funcional, esta vez escribiendo código Python limpio y explícito.

## H2 1. Configura tu entorno
Primero, preparemos tu entorno de desarrollo local. Crearemos una carpeta de proyecto dedicada, configuraremos un entorno virtual de Python para mantener nuestras dependencias aisladas e instalaremos el ADK.
Abre tu terminal y crea un nuevo directorio para tu proyecto. Navega dentro de él.

`mkdir adk-workshop-python`
`cd adk-workshop-python`

Primero aseguremonos que tenemos instalado Python en la maquina o workstation.
Si es en GCP verificar esta documentacion para instalarlo:

[Texto] https://docs.cloud.google.com/python/docs/setup?hl=es-419#linux

Crea un entorno virtual de Python. Esta es una práctica recomendada crucial para gestionar las dependencias del proyecto.

`python3 -m venv .venv`

Activa el entorno virtual. Deberás hacer esto cada vez que trabajes en este proyecto en una nueva sesión de terminal.


macOS / Linux:
`source .venv/bin/activate`

Windows:
`.venv\Scripts\activate`

Sabrás que está activo cuando veas (.venv) al principio del indicador de tu terminal.

Con tu entorno virtual activo, instala la librería google-adk usando pip.

`pip install google-adk`

Verifica la instalación comprobando la versión de ADK.

`adk --version`

Deberías ver una salida que indique el número de versión instalado.


** Consejo: ** Si no se encuentra el comando adk, verifica que tu entorno virtual esté activo. Deberías ver (.venv) en el indicador de tu terminal.


## H2 2. Crea tu proyecto de agente

Ahora la magia. Usaremos un solo comando de ADK para generar la estructura de un proyecto de agente completo basado en código.
Desde tu directorio adk-workshop-python (con el entorno virtual aún activo), ejecuta el siguiente comando:

`adk create --type=code mi_primer_agente`

Cuando solicita el modelo elijamos gemini-2.5-flash:

```
Choose a model for the root agent:
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

```
Enter Google Cloud project ID [xxxx-xxxx-xxxx]: 
xxxx-xxxx-xxxx
Enter Google Cloud region [us-central1]: 
us-central1

Agent created in /home/user/workshop-adk/solucion/adk-workshop-python/mi_primer_agente:
- .env
- __init__.py
- agent.py
```

El ADK ha creado un nuevo directorio llamado mi_primer_agente. Examinemos la estructura de archivos generada:

** mi_primer_agente/
├── .env
- __init__.py
└── agent.py
**

** agent.py: ** Este es el punto de entrada para nuestro agente. Escribiremos nuestro código Python aquí para definir y configurar el agente.
** .env: ** Este es un archivo especial para almacenar secretos, como nuestra clave de API.


Esta estructura limpia proporciona el punto de partida perfecto para construir un agente basado en Python.

## H2 3. Configura tu agente
Con el proyecto creado, escribamos el código para nuestro agente y proporcionémosle la clave de su cerebro.
Define el comportamiento del agente en Python
Ahora, abre el archivo mi_primer_agente/agent.py. Aquí es donde definirás programáticamente la personalidad y el propósito de tu agente.
Reemplaza el contenido del archivo con el siguiente código Python. Este código instancia un asistente servicial y creativo.


``` 
from google.adk.agents import Agent

# El entorno de ejecución de ADK busca un objeto llamado root_agent en main.py para iniciar la aplicación.
root_agent = Agent(
    model='gemini-2.5-flash',
    name="assistant_agent",
    description="Un asistente servicial y creativo para una amplia gama de tareas.",
    instruction="""
You are a friendly and knowledgeable assistant named Alex.
Your goal is to help users with their questions clearly and concisely.
When asked for creative tasks, like writing a poem or a joke, be imaginative!
"""
)
```

 
## H2 5. Ejecuta e interactúa con tu agente

¡El momento de la verdad! El proceso para ejecutar un agente basado en código es idéntico a uno basado en configuración, lo que resalta la unificación de herramientas de ADK.

Antes de ejecutarlo debes habilitar las APIs de Vertex
(Busca en la consola Vertex AI Studio y habilita las apis)


En tu terminal, navega hacia el directorio inicial desde donde creaste el agente (adk-workshop-python)

Ejecuta la interfaz web integrada de ADK.
` adk web `

Tu terminal mostrará una salida indicando que un servidor local se está ejecutando, generalmente en http://127.0.0.1:8080.

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)

```
Abre esta URL en tu navegador web. Verás la misma interfaz de chat limpia y sencilla que antes.
¡Empieza a chatear! Prueba los mismos comandos para ver a tu agente Python en acción:

¡Hola! ¿Cuál es tu nombre?
¿Cuál es el propósito principal del Google Agent Development Kit?
Escribe un poema corto sobre la construcción de un agente de IA.
Cuéntame un chiste de desarrolladores.

¡Ahora estás teniendo una conversación en tiempo real con el agente de IA que acabas de construir y definir completamente con Python! Cuando termines, detén el servidor presionando CTRL+C en tu terminal.

## H2 6. ¡Felicitaciones!
Has construido, configurado y ejecutado con éxito tu primer agente de IA mediante programación utilizando la librería ADK para Python.
Este enfoque basado en código es la puerta de entrada para desbloquear todo el potencial de ADK.  
