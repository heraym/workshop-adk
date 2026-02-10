 ### H1 Uso del Contexto con tu Agente en ADK

En este laboratorio aprenderás a gestionar la memoria a corto plazo o "de trabajo" dentro de una sola conversación utilizando objetos *** Contexto ***. Estos objetos —`ToolContext` y `CallbackContext`— son tu enlace directo al tiempo de ejecución de la sesión, lo que te permite leer y escribir datos sobre la marcha.

En este laboratorio, construirás un agente de "Lista de Compras Inteligente". Este agente utilizará `ToolContext` dentro de herramientas personalizadas para agregar elementos a una lista y verla. Luego, utilizará `CallbackContext` en un *callback* de ciclo de vida para guardar la lista final en un archivo, demostrando una potente combinación de gestión de estado y artefactos.

 

### H2 1. Configuración del Proyecto

Crea la estructura del proyecto:
`adk create --type=code mi_agente_de_compras`
Copia el siguiente código de inicio en `agent.py`. Esto define a nuestro agente, pero aún sin herramientas ni *callbacks*.

<!-- end list -->

``` python
# mi_agente_de_compras/agent.py (Código de inicio)

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types
import json

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Definiremos nuestras funciones de herramienta aquí
# def view_shopping_list(...):
#     pass
#
# def add_to_shopping_list(...):
#     pass

# Definiremos nuestra función de callback aquí
# async def save_list_as_artifact(...):
#     pass


# Definición del Agente
root_agent: Agent = Agent(
    model="gemini-2.5-flash",
    name="ShoppingListAgent",
    instruction="""Eres un asistente de lista de compras.
    - Usa la herramienta 'add_to_shopping_list' para agregar artículos.
    - Usa la herramienta 'view_shopping_list' para ver la lista actual.
    - Reconoce cuando se ha agregado un artículo.
    - Cuando el usuario pida "guardar la lista", responde con "OK, guardando tu lista."
    """,
    # Agregaremos herramientas y callbacks aquí
    tools=[],
    # after_agent_callback=...
)

```


*** Lectura de Estado con `ToolContext` ***

Démosle a nuestro agente la capacidad de ver lo que hay en la lista de compras. Crearemos una herramienta personalizada que lee un valor del `state` (estado) de la sesión. El objeto `ToolContext`, pasado automáticamente a cada función de herramienta, es nuestra puerta de enlace a este estado.

### H2. 2. Implementar la Herramienta `view_shopping_list`

En `agent.py`, descomenta e implementa la función `view_shopping_list`. Esta función accede a `tool_context.state` para obtener la lista. Se utiliza el método `.get()` para recuperar el valor de forma segura, proporcionando una lista vacía `[]` como valor predeterminado si la clave aún no existe.

``` python
# mi_agente_de_compras/agent.py

# ... (imports) ...

def view_shopping_list(tool_context: ToolContext) -> str:
    """Muestra los artículos actualmente en la lista de compras."""
    print("Executing tool: view_shopping_list")

    # Leer del estado usando el objeto context.
    # Proporcionar un valor predeterminado `[]` en caso de que la lista aún no se haya creado.
    current_list = tool_context.state.get("shopping_list", [])

    if not current_list:
        return "The shopping list is currently empty."

    # Formatear la lista para mostrarla al usuario.
    return "Here is your shopping list:\n- " + "\n- ".join(current_list)

# ... (rest of the code) ...

```

### H2 3.  Agregar la Herramienta al Agente

Ahora, actualiza la definición de `Agent` para incluir tu nueva herramienta.

``` python
# mi_agente_de_compras/agent.py

# ...

root_agent: Agent = Agent(
    # ... (name, model, instruction)
    tools=[
        FunctionTool(func=view_shopping_list),
    ],
    # after_agent_callback=...
)

```

Con esto implementado, el agente ahora puede entender una solicitud como "muéstrame mi lista", llamar a tu función de Python, y tu función leerá el estado de la sesión para proporcionar la respuesta.

*** Escritura de Estado con `ToolContext`  ***

Leer el estado es útil, pero escribir en él es lo que hace que un agente sea verdaderamente dinámico. Ahora implementaremos la herramienta `add_to_shopping_list`.

 Concepto Crítico: Debes modificar el estado de la sesión ***solo***  asignando valores al diccionario `state` en el objeto `Context` (por ejemplo, `tool_context.state['my_key'] = 'new_value'`). Esto indica el cambio al *framework* ADK, que luego registra correctamente la actualización en el historial de conversación. Nunca modifiques un objeto `Session` directamente.

### H2 4. Implementar la Herramienta `add_to_shopping_list`

Descomenta e implementa la función en `agent.py`. La lógica es simple: lee la lista actual, añade el nuevo artículo y luego vuelve a escribir toda la lista en el estado.

``` python
# mi_agente_de_compras/agent.py

# ...

def add_to_shopping_list(item: str, tool_context: ToolContext) -> str:
    """Añade un solo artículo a la lista de compras."""
    print(f"Executing tool: add_to_shopping_list with item '{item}'")

    # Leer la lista actual del estado
    current_list = tool_context.state.get("shopping_list", [])

    # Modificar la lista en memoria
    if item.lower() not in [i.lower() for i in current_list]:
        current_list.append(item)

    # Escribir la lista actualizada completa de vuelta al estado
    tool_context.state["shopping_list"] = current_list

    return f"'{item}' has been added to the list."

# ...

```

### H2 5. Agregar la Nueva Herramienta al Agente

Actualiza la lista de herramientas del agente para incluir la función de agregar.

``` python
# mi_agente_de_compras/agent.py

# ...

root_agent: Agent = Agent(
    # ... (name, model, instruction)
    tools=[
        FunctionTool(func=view_shopping_list),
        FunctionTool(func=add_to_shopping_list), # <-- AÑADIR ESTO
    ],
    # after_agent_callback=...
)

```

¡Tu agente ahora puede administrar una lista dentro de una sola conversación\!

*** Guardar Estado como un Artefacto con `CallbackContext` ***

¿Qué pasa si el usuario quiere una copia permanente de su lista? Podemos combinar nuestra gestión de estado con el concepto de **Artefactos**. Usaremos un *callback*, `after_agent_callback`, para guardar su lista. Los *callbacks* reciben un `CallbackContext`, que también tiene acceso a `state` y a los métodos de artefactos.

### H2 6. Implementar el Callback `save_list_as_artifact`

Esta función se ejecutará *después* de que el agente genere su respuesta final, recupera la lista del estado y la guarda como un artefacto de archivo de texto.

``` python
# mi_agente_de_compras/agent.py

# ...

async def save_list_as_artifact(callback_context: CallbackContext):
    """Después de que el agente se ejecute, verifica si el usuario pidió guardar la lista."""
    user_last_message = callback_context.user_content.parts[0].text

    print("Callback triggered: save_list_as_artifact")
    shopping_list = callback_context.state.get("shopping_list", [])

    if not shopping_list:
        print("List is empty, not saving artifact.")
        return

    # Preparar el contenido del artefacto
    file_content = "My Shopping List:\n\n- " + "\n- ".join(shopping_list)
    artifact_part = types.Part(text=file_content)

    # Usar el contexto para guardar el artefacto
    try:
        version = await callback_context.save_artifact(
                            filename="shopping_list.txt",
                            artifact=artifact_part
        )
        print(f"✅ Successfully saved shopping_list.txt as version {version}")
    except ValueError as e:
        print(f"🔴 Error saving artifact: {e}. Is an ArtifactService configured in your runner?")

# ...

```

### H2 7.  Agregar el Callback al Agente

Finalmente, conecta esta función al ciclo de vida del agente.

``` python
# mi_agente_de_compras/agent.py

# ...

root_agent: Agent = Agent(
    # ... (name, model, instruction, tools)
    after_agent_callback=save_list_as_artifact, # <-- AÑADIR ESTO
)

```

*** Ejecutar y Observar ***

Todo está ahora en su lugar. Solo necesitamos ejecutar nuestro agente usando `adk web`.

### H2 8. Código Final de `agent.py`

Aquí está el código completo para `mi_agente_de_compras/agent.py`.

``` python
# mi_agente_de_compras/agent.py (Código Final)

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def view_shopping_list(tool_context: ToolContext) -> str:
    """Muestra los artículos actualmente en la lista de compras."""
    print("Executing tool: view_shopping_list")
    current_list = tool_context.state.get("shopping_list", [])
    if not current_list:
        return "The shopping list is currently empty."
    return "Here is your shopping list:\n- " + "\n- ".join(current_list)

def add_to_shopping_list(item: str, tool_context: ToolContext) -> str:
    """Añade un solo artículo a la lista de compras."""
    print(f"Executing tool: add_to_shopping_list with item '{item}'")
    current_list = tool_context.state.get("shopping_list", [])
    if item.lower() not in [i.lower() for i in current_list]:
        current_list.append(item)
    tool_context.state["shopping_list"] = current_list
    return f"'{item}' has been added to the list."

async def save_list_as_artifact(callback_context: CallbackContext):
    print("Callback triggered: save_list_as_artifact")
    shopping_list = callback_context.state.get("shopping_list", [])
    if not shopping_list:
        print("List is empty, not saving artifact.")
        return
    file_content = "My Shopping List:\n\n- " + "\n- ".join(shopping_list)
    artifact_part = types.Part(text=file_content)
    try:
        version = await callback_context.save_artifact(
          filename="shopping_list.txt",
          artifact=artifact_part
        )
        print(f"✅ Successfully saved shopping_list.txt as version {version}")
    except ValueError as e:
        print(f"🔴 Error saving artifact: {e}. Is an ArtifactService configured in your runner?")

# Definición del Agente
root_agent: Agent = Agent(
    model="gemini-2.5-flash",
    name="ShoppingListAgent",
    instruction="""Eres un asistente de lista de compras.
    - Usa la herramienta 'add_to_shopping_list' para agregar artículos.
    - Usa la herramienta 'view_shopping_list' para ver la lista actual.
    - Reconoce cuando se ha agregado un artículo.
    - Cuando el usuario pida "guardar la lista", responde con "OK, guardando tu lista."
    """,
    tools=[
        FunctionTool(func=view_shopping_list),
        FunctionTool(func=add_to_shopping_list),
    ],
    after_agent_callback=save_list_as_artifact,
)

```

*** Ejecutar el Agente ***

1.  Desde tu terminal, navega al directorio que *contiene* tu carpeta `mi_agente_de_compras`.
2.  Ejecuta el comando `adk web`.

 

``` console
adk web

```

3.  Abre tu navegador web en `http://127.0.0.1:8080`.

### Interacción de Ejemplo

Habla con tu agente en la interfaz web. Prueba la siguiente conversación:

> **Tú:** agrega leche a mi lista
> 
> **Agente:** 'milk' has been added to the list.
> 
> **Tú:** agrega pan y huevos
> 
> **Agente:** 'bread' has been added to the list. 'eggs' has been added to the list.
> 
> **Tú:** muéstrame mi lista
> 
> **Agente:** Here is your shopping list:
> 
>   - milk
>   - bread
>   - eggs
> 
> **Tú:** ok por favor guarda la lista ahora
> 
> **Agente:** OK, saving your list.

Ahora, verifica tu terminal donde ejecutaste `adk web`. ¡Deberías ver los mensajes de registro de tus herramientas y, lo más importante, la confirmación de que el artefacto fue guardado\!

``` console
Executing tool: add_to_shopping_list with item 'milk'
Executing tool: add_to_shopping_list with item 'bread'
Executing tool: add_to_shopping_list with item 'eggs'
Executing tool: view_shopping_list
Callback triggered: save_list_as_artifact
✅ Successfully saved shopping_list.txt as version 0

```

## ¡Felicitaciones\!

Acabas de dominar uno de los conceptos más poderosos y esenciales en ADK para construir agentes interactivos complejos.

