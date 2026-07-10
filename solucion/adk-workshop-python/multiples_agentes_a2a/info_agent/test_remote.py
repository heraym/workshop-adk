import os
import asyncio
import time
import vertexai
from google.genai import types
from a2a.types import GetExtendedAgentCardRequest
from a2a.server.context import ServerCallContext
from agent import root_agent, info_agent_card, InfoAgentExecutor
from a2a.types import SendMessageRequest, Message, Part
from a2a.types import GetTaskRequest, TaskState
 
from vertexai.agent_engines.templates.a2a import A2aAgent, create_agent_card

PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"

BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}" 
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com"


async def test():
    remote_a2a_agent_resource_name = "projects/224237244779/locations/us-central1/reasoningEngines/1335139718387466240"
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


    message = Message(
        message_id=f"msg-{os.urandom(8).hex()}",
        role="ROLE_USER",
        parts=[Part(text="Cual es el precio del producto producto1?")],
    )

    request_params = SendMessageRequest(message=message)
    context = ServerCallContext()

    # Invoke the remote agent
    response = await remote_a2a_agent.on_message_send(request=request_params, context=context)
    task_object = None
    for chunk in response:
        if hasattr(chunk, "task") and chunk.task.id:
            task_object = chunk.task
            break

    if task_object:
        task_id = task_object.id
        print(f"Task started: {task_id}")
        print(f"Status: {task_object.status.state}")
    else:
        print("Could not retrieve the task object from the response.")


    request_params = GetTaskRequest(id=task_id, history_length=1)
    context = ServerCallContext()

    result = None
    retries = 0
    max_retries = 30

    while True:
        try:
            # Get the task result
            result = await remote_a2a_agent.on_get_task(request=request_params, context=context)

            if result.status.state in [TaskState.TASK_STATE_COMPLETED, TaskState.TASK_STATE_FAILED]:
                break

            print(f"Task state: {result.status.state}. Waiting 1s...")
            time.sleep(1)

        except Exception as e:
            error_str = str(e)
            if "400 Bad Request" in error_str:
                retries += 1
                if retries <= max_retries:
                    print(f"Received HTTP 400. Retrying in 1s ({retries}/{max_retries})...")
                    time.sleep(1)
                    continue
                else:
                    print("Max retries reached.")
                    raise
            else:
                raise

    # Artifacts contain the actual results
    for artifact in result.artifacts:
        if artifact.parts:
            part = artifact.parts[0]
            if hasattr(part, "text") and part.text:
                print(f"**Answer**:\n {part.text}")
            else:
                print("Could not extract text from artifact parts.")

if __name__ == "__main__":
    asyncio.run(test())