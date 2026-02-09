# H1 Ejecutar el agente en linea de comando

Vamos a ejecutar el agente que creamos en el lab 1 de otras formas. Por ejemplo en modo interactivo en linea de comando o desde un programa Python.
 
## H2 1. Terminal interactiva con adk run
El comando adk run es su herramienta principal para realizar pruebas rápidas y mantener conversaciones directas con su agente sin necesidad de abrir un navegador. Es una forma ligera y eficiente de verificar las instrucciones y el comportamiento de su agente.

Desde el directorio mi_primer_agente, simplemente ejecute el comando:

`adk run mi_primer_agente` 

El ADK cargará su root_agent desde main.py y le presentará un indicador interactivo.
`>`

Escriba un mensaje y presione Enter. El agente procesará su entrada e imprimirá su respuesta directamente en la terminal, luego presentará un nuevo indicador para su próximo mensaje.

```Ejemplo de Sesión:
> Hola! ¿Cuál es tu nombre?
Mi nombre es Alex. ¡Es un placer conocerte!
> Cuéntame un chiste sobre Python.
¿Por qué el desarrollador de Python usa gafas? Porque no puede ver C (C/see)#!
>
```

Esto crea una conversación continua donde el agente recuerda el contexto de la sesión actual, al igual que en la interfaz de usuario web.

Para salir de la sesión interactiva, puede escribir exit, quit, o presionar CTRL+D.
El comando adk run es una parte indispensable del flujo de trabajo de desarrollo para la iteración y el despliegue rápido.


## H2 2. Ejecución programática con Runner

Esta es la forma más potente de ejecutar a su agente. Al utilizar la clase Runner en su propio script de Python, puede integrar las capacidades de su agente en cualquier servicio backend, script automatizado o aplicación más grande. Obtiene un control total sobre la interacción.

Crear el Script del Runner
Dentro de su directorio mi_primer_agente, cree un nuevo archivo llamado run_programmatically.py.
Abra este nuevo archivo en su editor de código y agregue el siguiente código:

```
import asyncio
# Importe el agente que definió en main.py
from agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from dotenv import load_dotenv

# Cargue las variables de entorno desde el archivo .env
load_dotenv()

# Un nombre único para su aplicación.
APP_NAME = "mi_primer_app"

# IDs únicos para el usuario y la sesión de conversación.
USER_ID = "user_12345"
SESSION_ID = "session_67890"

async def main():
    """La función principal para ejecutar el agente de forma programática."""
    # 1. El Runner es el punto de entrada principal para ejecutar un agente.
    # Requiere el agente a ejecutar y un servicio de sesión para almacenar el historial.
    runner = Runner(
        agent=root_agent,
        session_service=InMemorySessionService(),
        app_name=APP_NAME
    )
    # 2. Se debe crear una sesión para mantener el historial de la conversación.
    print(f"Creando sesión: {SESSION_ID}")
    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    # 3. Prepare el mensaje del usuario en el formato ADK requerido.
    user_message = Content(parts=[Part(text="Escribe un haiku sobre APIs.")])
    print(f"Mensaje del usuario: '{user_message.parts[0].text}'")
    # 4. El método `run` ejecuta el agente y devuelve un flujo de eventos.
    print("\n--- Respuesta del Agente ---")
    final_response = ""
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_message
    ):

    # 5. Buscamos el evento "final response" para obtener la salida del agente.
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text.strip()
            print(final_response)
    print("--- Fin de la Respuesta ---\n")
# Ejecutar la función principal asíncrona.
if __name__ == "__main__":
    asyncio.run(main())
```


*** Ejecutar el Script ***
De vuelta en su terminal (en el directorio mi_primer_agente), ejecute su nuevo script de Python.

`python run_programmatically.py`

Verá la salida impresa directamente en su consola.
```
Creando sesión: session_67890
Mensaje del usuario: 'Escribe un haiku sobre APIs.'

--- Respuesta del Agente ---
Los datos fluyen,
Conectando mundos hoy,
Sutil enlace.
--- Fin de la Respuesta ---
```
¡Acaba de controlar con éxito a su agente de IA totalmente desde su propio código!
 
