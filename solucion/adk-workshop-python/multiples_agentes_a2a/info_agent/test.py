# Use the environment variable if the user doesn't provide Project ID.
import os
import asyncio

import vertexai
from google.genai import types
from agent import root_agent, info_agent_card, InfoAgentExecutor
from vertexai.agent_engines.templates.a2a import A2aAgent, create_agent_card

from a2a.types import GetExtendedAgentCardRequest
from a2a.server.context import ServerCallContext
from a2a.types import SendMessageRequest, Message, Part
from a2a.server.context import ServerCallContext

async def test():
    a2a_agent = A2aAgent(agent_card=info_agent_card, agent_executor_builder=InfoAgentExecutor, extended_agent_card=info_agent_card)
    a2a_agent.set_up()


    request = GetExtendedAgentCardRequest()
    context = ServerCallContext()

    response = await a2a_agent.on_get_extended_agent_card(
        request=request, context=context
    )

    print(response)

    message = Message(
        message_id=f"msg-{os.urandom(8).hex()}",
        role="ROLE_USER",
        parts=[Part(text="Cuanto sale el producto producto1?")],
    )
    message.metadata["user_id"] = "custom-user-123"

    request_params = SendMessageRequest(message=message)
    context = ServerCallContext()

    response = await a2a_agent.on_message_send(request=request_params, context=context)
    print(response)

if __name__ == "__main__":
    asyncio.run(test())