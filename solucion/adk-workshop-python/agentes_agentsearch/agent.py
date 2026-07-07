from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# Configuration
DATASTORE_ID = "projects/224237244779/locations/global/collections/default_collection/dataStores/tma-guias_1783454600240"

root_agent = Agent(
    name="vertex_search_agent",
    model="gemini-flash-latest",
    instruction="Answer questions using Agent Search to find information from internal documents. Always cite sources when available.",
    description="Enterprise document search assistant with Agent Search capabilities",
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)]
)