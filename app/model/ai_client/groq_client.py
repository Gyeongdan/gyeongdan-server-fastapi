import os
from typing import List, Optional

from groq import AsyncGroq

from app.config.loguru_config import logger
from app.model.ai_client.ai_client import AIClient, LLMModel


class GroqClient(AIClient):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GroqClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "ai_client"):
            self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    async def request(
        self,
        request_text: str,
        system_prompt: str,
        assistant_prompt: Optional[List[str]] = None,
        model: LLMModel = LLMModel.GROQ_LLAMA_3,
    ) -> str:
        if assistant_prompt is None:
            assistant_prompt = []

        target_model = self._get_model(model)
        messages = self._build_messages(system_prompt, assistant_prompt, request_text)

        completion = await self.client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=0.1,
            max_tokens=2500,
            top_p=0.5,
            stream=False,
            stop=None,
        )

        response_content = completion.choices[0].message.content
        logger.info(f"Completion: {completion}")
        return response_content

    def _get_model(self, model: LLMModel) -> str:
        model_mapping = {
            LLMModel.GROQ_LLAMA_3: "llama3-70b-8192",
        }

        if model in model_mapping:
            return model_mapping[model]
        raise ValueError(f"Unsupported model type: {model}")
