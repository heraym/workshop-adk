from google.adk.agents.llm_agent import Agent
# from my_model import *
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
import logging
from typing import Optional
from typing import Dict,AsyncGenerator
from google.adk.models import google_llm
 

source_app = ""
interaction_channel = ""
correlation_id = ""

async def process_query(callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Callback que toma el ultimo mensaje y obtiene el metadato. Esto va al modelo custom
    """

    # Inspect the last user message in the request contents
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")
    

    # La forma exacta de acceder a custom_metadata puede depender de la versión de ADK
    # y cómo se propaga el contexto. Aquí hay enfoques probables:

    custom_metadata = {}

    # Intenta obtenerlo desde invocation_context, que suele tener datos de la ejecución actual
    if hasattr(callback_context, 'invocation_context'):
         # Esto es especulativo: La estructura exacta dentro de invocation_context
         # puede variar. Podría estar directamente en la raíz o anidado.
         # Basado en notas, custom_metadata en 'input' debería estar disponible.
        if 'custom_metadata' in callback_context.invocation_context:
            custom_metadata = tool_ccallback_contextontext.invocation_context.get("custom_metadata", {})
        # A veces, todo el 'input' original está disponible
        elif 'input' in callback_context.invocation_context:
             custom_metadata = callback_context.invocation_context['input'].get("custom_metadata", {})

    source_app = custom_metadata.get("source_app")
    callback_context.state["source_app"] = source_app
    interaction_channel = custom_metadata.get("interaction_channel")
    correlation_id = custom_metadata.get("correlation_id")

    if source_app:
        logging.info(f"  Origen de la aplicación: {source_app}")
    if interaction_channel:
        logging.info(f"  Canal de interacción: {interaction_channel}")
    if correlation_id:
        logging.info(f"  ID de correlación: {correlation_id}")

    return None

async def process_state(callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Callback que toma el ultimo mensaje y obtiene el metadato. Esto va al modelo custom
    """
    custom_metadata = {}

    source_app = callback_context.state.get("source_app")
    interaction_channel = callback_context.state.get("interaction_channel")
    correlation_id = callback_context.state.get("correlation_id")

    llm_request.config.labels= {"source_app" : source_app}

    if source_app:
        logging.info(f"  Origen de la aplicación: {source_app}")
    if interaction_channel:
        logging.info(f"  Canal de interacción: {interaction_channel}")
    if correlation_id:
        logging.info(f"  ID de correlación: {correlation_id}")

    return None

class LabeledGemini(google_llm.Gemini):
    
    labels: Dict[str, str] = {}
    
    async def generate_content_async(
        self,
        llm_request: LlmRequest,
        stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        async for llm_response in super().generate_content_async(llm_request, stream):
            yield llm_response
async def _preprocess_request(self, llm_request: LlmRequest) -> None:
        if llm_request.config and self.labels:
            llm_request.config.labels = self.labels
        await super()._preprocess_request(llm_request)

my_model = LabeledGemini(
    model_name="gemini-2.5-flash",
    labels={
        "source_app": "acme_corp",
        "interaction_channel": "mobile",
        "correlation_id": "0" 
    }
)

root_agent = Agent(
    model= "gemini-2.5-flash",
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    before_model_callback=process_state 
)

 