# cleanup.py

from vertexai import agent_engines

AGENT_RESOURCE_NAME = "projects/224237244779/locations/us-central1/reasoningEngines/714784812635783168" # Pega tu nombre de recurso aquí

print(f"Deleting agent: {AGENT_RESOURCE_NAME}")
remote_app = agent_engines.get(AGENT_RESOURCE_NAME)
remote_app.delete(force=True) # force=True también elimina recursos hijos como sesiones`

print("Agent deleted.")