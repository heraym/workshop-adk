# scripts/resolve_agent_card_url.py
import asyncio
import os
from pathlib import Path

import vertexai
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

#PROJECT_ID = "genai-demos-432617"
PROJECT_ID = "224237244779"
REGION = "us-central1"
RESOURCE_NAME = "projects/224237244779/locations/us-central1/reasoningEngines/3109153351292420096"


async def main():
    vertexai.init(project=PROJECT_ID, location=REGION)
    client = vertexai.Client(
        project=PROJECT_ID, location=REGION,
        http_options=types.HttpOptions(api_version="v1beta1"),
    )
 
    remote_agent = client.agent_engines.get(name=RESOURCE_NAME)
    print("Remote Agent:", remote_agent)
    card = await remote_agent.handle_authenticated_agent_card()
    card_url = f"{card.url}/v1/card"

    print(f"Agent: {card.name}")
    print(f"Card URL: {card_url}")


if __name__ == "__main__":
    asyncio.run(main())