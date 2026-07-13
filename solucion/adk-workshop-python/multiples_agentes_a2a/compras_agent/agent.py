# agents/orchestrator_agent.py
import httpx
import google.auth
from google.auth.transport.requests import Request
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import llm_agent
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from dotenv import load_dotenv
import vertexai
from google.genai import types
from google.adk.integrations.agent_registry import AgentRegistry


from a2a.server.context import ServerCallContext

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar el Cliente del Agente Remoto
remote_a2a_agent_resource_name = "projects/genai-demos-432617/locations/us-central1/agents/agentregistry-00000000-0000-0000-4a55-929d073e8d70" 

PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"

BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}" 
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com"

config = {"http_options": {"base_url": ENDPOINT}}


# Define the GoogleAuth class for the HTTP client
class GoogleAuth(httpx.Auth):
    def __init__(self):
        self.creds, _ = google.auth.default()
    def auth_flow(self, request):
        if not self.creds.valid:
            self.creds.refresh(Request())
        request.headers["Authorization"] = f"Bearer {self.creds.token}"
        yield request


# Initialize the Gen AI client using http_options
# The parameter customizes how the Agent Platform client communicates with Google Cloud's backend services.
# It's used here to access new, pre-release features.
 

registry = AgentRegistry(
    project_id=PROJECT_ID,
    location=LOCATION,
)

httpx_client = httpx.AsyncClient(auth=GoogleAuth(), timeout=httpx.Timeout(60.0))
remote_info_agent = registry.get_remote_a2a_agent(
    agent_name=remote_a2a_agent_resource_name,
    httpx_client=httpx_client
)

root_agent = LlmAgent(
            name="compras_agent",
            model='gemini-2.5-flash',
            description='Un agente para vender productos.',
            instruction=f'''Sos un agente que vende productos. Tenes que determinar que producto quiere el cliente y en que cantidad.
    Si te pide el cliente informacion de un producto o el precio, se la podes brindar con el agente "remote_info_agent".''',
            sub_agents=[remote_info_agent],
)