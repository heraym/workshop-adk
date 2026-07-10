import asyncio
import vertexai
from google.genai import types
from a2a.types import GetExtendedAgentCardRequest
from a2a.server.context import ServerCallContext
from agent import root_agent, info_agent_card, InfoAgentExecutor
from a2a.types import SendMessageRequest, Message, Part
 
from vertexai.agent_engines.templates.a2a import A2aAgent, create_agent_card

PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"

BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}" 
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com"


async def test():
    remote_a2a_agent_resource_name = "projects/224237244779/locations/us-central1/reasoningEngines/7472983060540030976"
    config = {"http_options": {"base_url": ENDPOINT}}
    
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

    remote_a2a_agent = client.agent_engines.get(
        name= remote_a2a_agent_resource_name,
        config=config,
    )

    request = GetExtendedAgentCardRequest()
    context = ServerCallContext()

    remote_a2a_agent_card = await remote_a2a_agent.on_get_extended_agent_card(
        request=request, context=context
    )

    print(f"Agent: {remote_a2a_agent_card.name}")   
    print(f"Supported Interfaces: {remote_a2a_agent_card.supported_interfaces}")
    print(f"Skills: {[s.description for s in remote_a2a_agent_card.skills]}")
    print(f"Examples: {[s.examples for s in remote_a2a_agent_card.skills][0]}")


if __name__ == "__main__":
    asyncio.run(test())