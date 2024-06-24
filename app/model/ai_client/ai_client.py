from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional


class LLMModel(str, Enum):
    OPENAI_GPT4o = "OPENAI_GPT4o"
    GROQ_LLAMA_3 = "GROQ_LLAMA_3"


class AIClient(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        pass

    @abstractmethod
    async def request(
        self,
        request_text: str,
        system_prompt: str,
        assistant_prompt: Optional[List[str]],
        model: LLMModel,
    ) -> str:
        pass

    @abstractmethod
    def _get_model(self, model: LLMModel) -> str:
        pass

    @staticmethod
    def _build_messages(
        system_prompt: str, assistant_prompt: List[str], request_text: str
    ) -> List[dict]:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(
            {"role": "assistant", "content": prompt} for prompt in assistant_prompt
        )
        messages.append({"role": "user", "content": request_text})
        return messages
