import os
from google.adk.integrations.agent_registry import AgentRegistry
from google.auth import default
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

_, project_id = default()
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "agentregistry-00000000-0000-0000-5c77-00a5d3ff3187")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
registry = AgentRegistry(project_id=project_id, location=LOCATION)

mcp_toolset = registry.get_mcp_toolset(
    f"projects/genai-demos-432617/locations/us-central1/mcpServers/agentregistry-00000000-0000-0000-5c77-00a5d3ff3187"
)

root_agent = Agent(
        name="Agente Matematico 2",
        description=(
            "You are a helpful AI Assistant who can answer questions."
        ),
        model=Gemini(
            model='gemini-2.5-flash',
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        tools=[mcp_toolset],
)