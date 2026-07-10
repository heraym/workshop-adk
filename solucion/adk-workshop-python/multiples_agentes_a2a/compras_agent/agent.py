# agents/orchestrator_agent.py
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv

from a2a.types import GetExtendedAgentCardRequest
from a2a.server.context import ServerCallContext

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar el Cliente del Agente Remoto
remote_a2a_agent_resource_name = "projects/224237244779/locations/us-central1/reasoningEngines/1335139718387466240"
config = {"http_options": {"base_url": ENDPOINT}}

PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"

BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}" 
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com"

# Initialize Agent Platform session
vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=BUCKET_URI,
        api_endpoint=ENDPOINT,  # This directs requests to the {$ENV} endpoint
)

# Initialize the Gen AI client using http_options
# The parameter customizes how the Agent Platform client communicates with Google Cloud's backend services.
# It's used here to access new, pre-release features.
client = vertexai.Client(
        project=PROJECT_ID,
        location=LOCATION,
        http_options=types.HttpOptions(api_version="v1beta1", base_url=f"{ENDPOINT}/"),
)

remote_info_agent = client.agent_engines.get(
    name=remote_a2a_agent_resource_name,
    config=config,
)

# Definir el Agente Orquestador
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='orchestrator_agent',
    description='Un agente para vender productos.',
    instruction=f'''Sos un agente que vende productos. Tenes que determinar que producto quiere el cliente y en que cantidad.
    Si te pide el cliente informacion de un producto o el precio, se la podes brindar con el agente "remote_info_agent".''',
    # El agente remoto se trata igual que un sub-agente
    sub_agents=[
        remote_info_agent
    ],
)