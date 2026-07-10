from google.adk.agents.llm_agent import Agent
from a2a.types import AgentCard

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import VertexAiSessionService

from google.genai import types 


# Agent Engine
from vertexai.agent_engines.templates.a2a import A2aAgent, create_agent_card
from a2a.client import ClientConfig, ClientFactory
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a import types as a2a_types
from a2a.utils import TransportProtocol
import os
import vertexai
from google.adk.runners import Runner


def info_producto(producto: str) -> str:
    """Provee informacion y precio de un producto particular.

    Args:
        producto: El codigo de producto.

    Returns:
        La descripcion del producto y el precio.
    """
    if "producto1" in producto.lower() or "1" in producto.lower():
        return { "producto": { "descripcion": "Este es el producto 1", "precio": 100} }
    if "producto2" in producto.lower() or "2" in producto.lower():
        return { "producto": { "descripcion": "Este es el producto 2", "precio": 500} }
    if "producto3" in producto.lower() or "3" in producto.lower():
        return { "producto": { "descripcion": "Este es el producto 3", "precio": 10} }
    return 0

root_agent = Agent(
    model='gemini-2.5-flash',
    name='info_agent',
    description='Un agente que provee informacion de los productos.',
    instruction='Debes proveer informacion de los productos por los que te consultan. Para eso debes usar la tool "info_producto"',
    tools=[info_producto]
)

# Define a skill - a specific capability your agent offers
# Agents can have multiple skills for different tasks
info_agent_skill = a2a_types.AgentSkill(
    # Unique identifier for this skill
    id="info_prod",
    # Human-friendly name
    name="Info de Productos",
    # Detailed description helps clients understand when to use this skill
    description="Obtener informacion de productos",
    # Tags for categorization and discovery
    # These help in agent marketplaces or registries
    tags=["info", "productos", "precio"],
    # Examples show clients what kinds of requests work well
    # This is especially helpful for LLM-based clients
    examples=[
        "Cual es el precio del producto producto1?",
        "Que es el producto producto2?",
    ],
    # Optional: specify input/output modes
    # Default is text, but could include images, files, etc.
    input_modes=["text/plain"],
    output_modes=["text/plain"],
)

# Use the helper function to create a complete Agent Card
info_agent_card = create_agent_card(
    agent_name="Info Agent",
    description="Agente que provee info de productos",
    skills=[info_agent_skill],
)



class InfoAgentExecutor(AgentExecutor):
    """Refactored Executor using VertexAiSessionService for persistence."""

    def __init__(self) -> None:
        self.agent = None
        self.runner = None

    def _init_agent(self) -> None:
        if self.agent is None:
            # 1. Initialize Agent Platform using environment-injected metadata
            project = os.environ.get("GOOGLE_CLOUD_PROJECT")
            location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            # This ID is automatically provided by Agent Engine at runtime
            engine_id = os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID")

            vertexai.init(project=project, location=location)

            self.agent = root_agent

            # 2. Initialize the Session Service
            # If engine_id exists, we are deployed remotely -> use VertexAiSessionService.
            # If engine_id is None, we are local -> use InMemorySessionService.
            if engine_id:
                session_service = VertexAiSessionService(
                    project=project, location=location, agent_engine_id=engine_id
                )
            else:
                from google.adk.sessions.in_memory_session_service import (
                    InMemorySessionService,
                )

                session_service = InMemorySessionService()

            # 3. Setup Runner with the session service
            self.runner = Runner(
                app_name=self.agent.name,
                agent=self.agent,
                artifact_service=InMemoryArtifactService(),
                session_service=session_service,
                memory_service=InMemoryMemoryService(),
            )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if self.agent is None:
            self._init_agent()

        query = context.get_user_input()
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        user_id = (
            context.message.metadata["user_id"]
            if "user_id" in context.message.metadata
            else "vais-query-reasoning-engine"
        )

        task = a2a_types.Task(
            id=context.task_id,
            context_id=context.context_id,
            status=a2a_types.TaskStatus(
                state=a2a_types.TaskState.TASK_STATE_SUBMITTED
            ),
            history=[context.message] if context.message else [],
        )
        await event_queue.enqueue_event(task)

        await updater.start_work()

        try:
            # Using context_id (A2A) as session_id (Vertex) ensures continuity
            session = await self._get_or_create_session(context.context_id, user_id)

            content = types.Content(role="user", parts=[types.Part(text=query)])

            async for event in self.runner.run_async(
                session_id=session.id,
                user_id=user_id,
                new_message=content,
            ):
                if event.is_final_response():
                    answer = self._extract_answer(event)
                    await updater.add_artifact(
                        [a2a_types.Part(text=answer)],
                        name="answer",
                        last_chunk=True,
                    )
                    await updater.complete()
                    break

        except Exception as e:
            await updater.update_status(
                a2a_types.TaskState.TASK_STATE_FAILED,
                message=updater.new_agent_message(
                    [a2a_types.Part(text=f"An error occurred: {str(e)}")]
                ),
            )
            raise

    async def _get_or_create_session(self, context_id: str, user_id: str):
        engine_id = os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID")
        app_name = engine_id if engine_id else self.agent.name

        session = await self.runner.session_service.get_session(
            app_name=app_name,
            session_id=context_id,
            user_id=user_id,
        )

        if not session:
            session = await self.runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
            )
        return session

    def _extract_answer(self, event) -> str:
        parts = event.content.parts
        text_parts = [part.text for part in parts if part.text]
        return " ".join(text_parts) if text_parts else "No answer found."

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle task cancellation requests."""
        task_id = context.task_id
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=task_id or "",
            context_id=context.context_id or "",
        )
        await updater.cancel()