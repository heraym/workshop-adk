 


export OTEL_SERVICE_NAME="Agente de Compras"
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"
export OTEL_SEMCONV_STABILITY_OPT_IN="gen_ai_latest_experimental"
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT="EVENT_ONLY"

adk deploy agent_engine --project=genai-demos-432617 --region=us-central1 --display_name="Agente de Compras A2A"  --trace_to_cloud --otel_to_cloud compras_agent



********
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/agents/agent_engine/tutorial_a2a_on_agent_engine.ipynb