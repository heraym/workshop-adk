# deploy_with_tracing.py

import os
import vertexai
from vertexai import agent_engines
from agents.agent import root_agent

# Configuration
PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"
BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}"

def deploy_agent():
    """Deploys the ADK agent with Cloud Trace enabled."""
    print(f"Initializing Vertex AI for project '{PROJECT_ID}'...")
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=BUCKET_URI,
    )

    print("Wrapping agent in AdkApp with tracing enabled...")

    # --- ESTA ES LA CLAVE ---
    # El flag `enable_tracing=True` configura automáticamente el agente
    # para enviar rastros de OpenTelemetry a Google Cloud Trace.
    app = agent_engines.AdkApp(
        agent=root_agent,
        enable_tracing=true,
    )
    # -----------------------

    print("Starting deployment... This may take 5-10 minutes.")
    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        display_name="Traced Weather Agent",
        extra_packages=["agents"]
    )

    print("\n--- Deployment finished! ---")
    print(f"Deployed Agent Resource Name: {remote_app.resource_name}")

if __name__ == "__main__":
    deploy_agent()
