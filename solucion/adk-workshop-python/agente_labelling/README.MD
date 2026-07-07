Deployar el agente:

adk deploy agent_engine    --project="genai-demos-432617"  --region="us-central1" --display_name="Agente Labelling" --trace_to_cloud   --otel_to_cloud --agent_engine_id=projects/224237244779/locations/us-central1/reasoningEngines/4280054070036660224 agente_labelling

Para invocar al agente:

curl \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    https://us-central1-aiplatform.googleapis.com/v1/projects/224237244779/locations/us-central1/reasoningEngines/4280054070036660224:query \
    -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'

curl \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    https://us-central1-aiplatform.googleapis.com/v1/projects/224237244779/locations/us-central1/reasoningEngines/4280054070036660224:streamQuery?alt=sse -d '{
"class_method": "async_stream_query",
"input": {
    "user_id": "u_123",
    "session_id": "5528684007392280576",
    "message": "Hola como estas?",
    
 "state_delta": { "source_app": "app1", "interaction_channel": "web", "correlation_id": "1"}   
}
}'

***************************************************
Vamos a correr