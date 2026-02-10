 # deploy.py

import os
import vertexai
from vertexai import agent_engines

# Import the agent we defined in the other file

from agents.agent import root_agent

# Configuration

PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"
BUCKET_NAME = "agent-engine-workshop"

BUCKET_URI = f"gs://{BUCKET_NAME}"

def deploy_agent():

  """Packages and deploys the ADK agent to Vertex AI Agent Engine."""

  print(f"Initializing Vertex AI for project '{PROJECT_ID}' in '{LOCATION}'...")
  
  # Initialize the Vertex AI SDK
  vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=BUCKET_URI,
  )

  # Wrap the ADK agent in an AdkApp object

  # This makes it compatible with Agent Engine and handles session management.

  print("Wrapping agent in AdkApp...")

  app = agent_engines.AdkApp(
    agent=root_agent,
  )


  # Deploy the application
  # This packages the code, builds a container, and deploys it.
  # This process can take several minutes.

  print("Starting deployment to Agent Engine... This may take 5-10 minutes.")

  remote_app = agent_engines.create(
     agent_engine=app,
     # Tell Agent Engine which libraries to install in the managed environment.
     requirements=["google-cloud-aiplatform[adk,agent_engines]"],
     display_name="My Weather Agent", 
     extra_packages=["agents"]
  )

  print("\n--- Deployment finished! ---")
  print(f"Deployed Agent Resource Name: {remote_app.resource_name}")

if __name__ == "__main__":
   deploy_agent()
