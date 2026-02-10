# H1  Manejo de Sesiones en Agentes

 Uno de los temas mas importantes en el desarrollo de agentes son la gestion de la memoria del agente, ya sea de corto-termino (Session) o de largo-termino (Memory)
 
 En este lab vamos a usar tools ya preconstruidas para ver como podemos por ejemplo, guardar las sesiones de un agente en memoria de largo termino, para hacer un agente que "recuerde" todas las conversaciones.
  
## H2 1. Creamos el agente
En el directorio del workshop vamos a crear un agente mi_agente_memorioso

`adk create --type=code mi_agente_memorioso`

Y vamos a editar el archivo agent.py.

```
from google import adk
from google.adk.agents.llm_agent import Agent



root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Tenes que responder cualquier pregunta que te hagan. Si ya te hicieron esa pregunta antes, entonces responde "Ya te lo dije! No me hagas perder tiempo"'
)


```

Este agente, me permite probar cuanto "recuerda" un agente normal.
Si yo le hago la misma pregunta durante una sesion me respondera "Ya te lo dije! No me hagas perder tiempo".
Pero si le pregunto lo mismo en distintas sesiones me va a contestar nuevamente.

  
## H2 2. Haciendolo "memorioso"

Para que el agente "recuerde" lo que le pregunte en otras sesiones, hay que usar la tool preload_memory_tool (que carga la memoria completa al inicio) y armar un callback para auto-grabar la sesion en la memoria al finalizar cada sesion. 
El agente quedaria asi:

```
from google import adk
from google.adk.agents.llm_agent import Agent
from google.adk.tools import load_memory 
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Tenes que responder cualquier pregunta que te hagan. Si ya te hicieron esa pregunta antes, entonces responde "Ya te lo dije! No me hagas perder tiempo"',
    tools=[PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)

```

 