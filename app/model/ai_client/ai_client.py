from abc import ABC, abstractmethod
from enum import Enum


class LLMModel(str, Enum):
    OPENAI_GPT4o = "OPENAI_GPT4o"
    GROQ_LLAMA_3 = "GROQ_LLAMA_3"


class AIClient(ABC):
    @abstractmethod
    async def request(
        self,
        request_text: str,
        system_prompt: str,
        assistant_prompt: list[str],
        model: LLMModel,
    ) -> str:
        pass
