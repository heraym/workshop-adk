import os
from google.adk.integrations.agent_registry import AgentRegistry
from google.auth import default
from google.adk.agents import Agent
from google.genai import types

_, project_id = default()
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "agentregistry-00000000-0000-0000-2552-efbe88faad84")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
registry = AgentRegistry(project_id=project_id, location=LOCATION)

mcp_toolset = registry.get_mcp_toolset(
    f"projects/genai-demos-432617/locations/global/mcpServers/agentregistry-00000000-0000-0000-2552-efbe88faad84"
)

root_agent = Agent(
        name="viajes",
        description=(
            "A helpful assistant for planning travel routes."
        ),
        model='gemini-2.5-flash',
        tools=[mcp_toolset],
)