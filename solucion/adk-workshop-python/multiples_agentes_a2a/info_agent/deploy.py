# Use the environment variable if the user doesn't provide Project ID.
import os

import vertexai
from google.genai import types
from agent import root_agent

# fmt: off
PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"

BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}"

ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com"


# !gsutil mb -l $LOCATION -p $PROJECT_ID $BUCKET_URI

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

remote_a2a_agent = client.agent_engines.create(
    # The actual agent to deploy
    agent=root_agent,
    config={
        # Display name shown in the console
        "display_name": "Info Agent",
        # Description for documentation
        "description": "Agente que provee info de productos",
        # Python dependencies needed in Agent Engine
        "requirements": [
            "a2a-sdk>=1.0.0",
            "google-cloud-aiplatform[agent_engines,adk]>=1.156.0",
            "cloudpickle==3.1.1",
            "pydantic==2.11.7",
        ],
        "extra_packages": ["."],
        "env_vars": {
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
        },
        # Http options
        "http_options": {
            "base_url": ENDPOINT,
            "api_version": "v1beta1",
        },
        # Staging bucket
        "staging_bucket": BUCKET_URI,
        "min_instances": 1,
        "max_instances": 1
    },
)
