from google.adk.agents.llm_agent import Agent
import os

os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

root_agent = Agent(
    model='gemini-live-2.5-flash-native-audio',
    name="assistant_agent",
    description="Un asistente servicial y creativo para una amplia gama de tareas.",
    instruction="""
You are a friendly and knowledgeable assistant named Alex.
Your goal is to help users with their questions clearly and concisely.
When asked for creative tasks, like writing a poem or a joke, be imaginative!
"""
)
 