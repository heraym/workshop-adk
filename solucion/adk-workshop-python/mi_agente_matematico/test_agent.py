# test_deployed_agent.py

import asyncio
from vertexai import agent_engines

# TODO: Paste the Resource Name from the deployment script output here

AGENT_RESOURCE_NAME = "projects/224237244779/locations/us-central1/reasoningEngines/5081004310406365184"
async def main():

  """Connects to the deployed agent and sends a query."""
  print(f"Connecting to remote agent: {AGENT_RESOURCE_NAME}")
  
  # Get a client handle to the remote application

  remote_app = agent_engines.get(AGENT_RESOURCE_NAME)


  i = 1
  while i < 10:
    # Create a remote session to maintain conversation history
    print("Creating new remote session...")
    remote_session = await remote_app.async_create_session(user_id="test-user-123")
    print(f"Session created with ID: {remote_session['id']}")

    # Send a query to the agent

    prompt = "Cuanto es 8 + 8?"
    print(f"\nSending prompt: '{prompt}'")

    print("\n--- Agent Response Stream ---")
    async for event in remote_app.async_stream_query(
       user_id="test-user-123",
       session_id=remote_session["id"],
       message=prompt,
    ):

      print(event)
    
    prompt = "Cuanto es 3 + 4?"
    print(f"\nSending prompt: '{prompt}'")

    print("\n--- Agent Response Stream ---")
    async for event in remote_app.async_stream_query(
       user_id="test-user-123",
       session_id=remote_session["id"],
       message=prompt,
    ):

      print(event)
  
    print("--- End of Stream ---")
    i += 1
  

if __name__ == "__main__":
    asyncio.run(main())