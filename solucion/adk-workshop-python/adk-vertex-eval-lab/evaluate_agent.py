# evaluate_agent.py

import os
import json
import asyncio
import pandas as pd

import vertexai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService
from google.genai import types
from vertexai.preview.evaluation import EvalTask
from vertexai.preview.evaluation.metrics import (
    PointwiseMetric,
    PointwiseMetricPromptTemplate,
    TrajectorySingleToolUse,
)

# --- Configuration ---
PROJECT_ID = "genai-demos-432617"
LOCATION = "us-central1"
BUCKET_NAME = "agent-engine-workshop"
BUCKET_URI = f"gs://{BUCKET_NAME}"


# Set environment variables for ADK
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"



# Configure Vertex AI Experiment name
EXPERIMENT_NAME = "adk-product-agent-evaluation"

print("Configuration loaded.")

def get_product_details(product_name: str) -> str:
    """Gathers basic details about a product."""
    details = {
        "productx": "A cutting-edge smartphone with advanced camera features.",
        "producty": "High-performance running shoes designed for comfort and speed.",
    }
    return details.get(product_name.lower(), "Product details not found.")

def get_product_price(product_name: str) -> str:
    """Gathers the price of a product."""
    prices = {"productx": "500 USD", "producty": "100 USD"}
    return prices.get(product_name.lower(), "Product price not found.")

def build_agent():
    """Builds and returns the ADK agent."""
    return Agent(
        name="ProductResearchAgent",
        model="gemini-2.5-flash",
        description="An agent that performs product research.",
        instruction="You must use the available tools to answer user questions about product price or details.",
        tools=[get_product_details, get_product_price],
    )

print("Agent definition ready.")

async def run_agent_async(prompt: str, agent: Agent) -> dict:
    """Runs the ADK agent for a given prompt and parses the output."""
    runner = Runner(
        agent=agent, app_name="eval_app", session_service=InMemorySessionService()
    )
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    await runner.session_service.create_session(
        app_name="eval_app", user_id="eval_user", session_id="eval_session"
    )

    events = [
        event
        async for event in runner.run_async(
            user_id="eval_user", session_id="eval_session", new_message=content
        )
    ]

    # Parse the event stream to find the final response and tool calls
    final_response = ""
    trajectory = []
    for event in events:
        if not getattr(event, "content", None) or not getattr(
            event.content, "parts", None
        ):
            continue
        for part in event.content.parts:
            if getattr(part, "function_call", None):
                info = {
                    "tool_name": part.function_call.name,
                    "tool_input": dict(part.function_call.args),
                }
                if info not in trajectory:
                    trajectory.append(info)
            if event.content.role == "model" and getattr(part, "text", None):
                final_response = part.text.strip()
    print(final_response)
    print(json.dumps(trajectory))
    return {
        "response": final_response,
        "predicted_trajectory": json.dumps(trajectory),  # Must be a JSON string
    }

def agent_runner_sync(prompt: str):
    """Synchronous wrapper for the async agent runner."""
    # This is a bit of a trick to run our main async function from the sync context
    # of the evaluation library.
    agent = build_agent()
    result = asyncio.run(run_agent_async(prompt, agent))
    return result

print("Agent runner function defined.")

def get_eval_dataset():
    """Creates a pandas DataFrame with evaluation data."""
    eval_data = {
        "prompt": [
            "How much does the productx cost?",
            "Tell me about the producty.",
        ],
        "reference_trajectory": [
            [{"tool_name": "get_product_price", "tool_input": {"product_name": "productx"}}],
            [{"tool_name": "get_product_details", "tool_input": {"product_name": "producty"}}],
        ],
    }
    df = pd.DataFrame(eval_data)
    # The evaluation service expects the trajectory to be a JSON string
    df["reference_trajectory"] = df["reference_trajectory"].apply(json.dumps)
    return df

def get_eval_metrics():
    """Defines the metrics for the evaluation task."""
    # Metric 1: Check if the correct single tool was used.
    tool_metric = TrajectorySingleToolUse(tool_name="get_product_price")

    # Metric 2: A custom, model-based metric to judge response quality.
    criteria = {
        "Follows trajectory": (
            "Evaluate whether the agent's response logically follows from the "
            "sequence of actions it took. Does the response reflect the information "
            "gathered by the tool?"
        )
    }
    rating_rubric = {"1": "Follows trajectory", "0": "Does not follow trajectory"}

    prompt_template = PointwiseMetricPromptTemplate(
        criteria=criteria,
        rating_rubric=rating_rubric,
        input_variables=["prompt", "predicted_trajectory"],
    )

    response_metric = PointwiseMetric(
        metric="response_follows_trajectory",
        metric_prompt_template=prompt_template,
    )

    return [tool_metric, response_metric]

print("Evaluation dataset and metrics defined.")

def main():
    """Main function to run the evaluation pipeline."""
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=BUCKET_URI, experiment=EXPERIMENT_NAME)

    # Create GCS bucket if it doesn't exist
    print(f"Checking for GCS bucket: {BUCKET_URI}")
    os.system(f"gsutil ls -b {BUCKET_URI} || gsutil mb -l {LOCATION} {BUCKET_URI}")

    # Get dataset and metrics
    eval_dataset = get_eval_dataset()
    eval_metrics = get_eval_metrics()

    print("\n--- Starting Evaluation Task ---")
    print(f"Dataset has {len(eval_dataset)} rows.")

    # Create the evaluation task
    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=eval_metrics,
        experiment=EXPERIMENT_NAME
    )

    # Run the evaluation
    eval_result = eval_task.evaluate(
        runnable=agent_runner_sync,
        experiment_run_name="product-agent-run-6"
    )

    print("\n--- Evaluation Complete ---")
    print("Summary Metrics:")
    print(pd.DataFrame(eval_result.summary_metrics.items(), columns=["Metric", "Value"]))


if __name__ == "__main__":
    main()