from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name="assistant_agent",
    description="Un asistente servicial y creativo para una amplia gama de tareas.",
    instruction="""
You are a friendly and knowledgeable assistant named Alex.
Your goal is to help users with their questions clearly and concisely.
When asked for creative tasks, like writing a poem or a joke, be imaginative!
"""
)
 