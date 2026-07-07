from typing import Dict,AsyncGenerator
from google.adk.agents.llm_agent import Agent
from google.adk.models import google_llm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse


class LabeledGemini(google_llm.Gemini):
    
    labels: Dict[str, str] = {}
    
    async def generate_content_async(
        self,
        llm_request: LlmRequest,
        stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        async for llm_response in super().generate_content_async(llm_request, stream):
            yield llm_response
async def _preprocess_request(self, llm_request: LlmRequest) -> None:
        if llm_request.config and self.labels:
            llm_request.config.labels = self.labels
        await super()._preprocess_request(llm_request)