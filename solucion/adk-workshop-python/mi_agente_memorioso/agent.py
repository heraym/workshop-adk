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
