from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.groq_client import GroqClient
from app.model.ai_client.openai_client import OpenAIClient


def get_platform_client(model: LLMModel):
    model_name = model.name
    if model_name.startswith("GROQ"):
        return GroqClient()
    if model_name.startswith("OPENAI"):
        return OpenAIClient()

    raise ValueError(f"Unsupported API type: {model}")
