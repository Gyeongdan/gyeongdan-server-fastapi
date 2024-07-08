from dotenv import load_dotenv

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.service.public_data_api_service import PublicDataAPI, PublicDataAPIService
from app.utils.json_parser import parse


class PublicDataArticleService:
    async def public_data_to_article(self, publicDataApi: PublicDataAPI):
        load_dotenv()
        ai_client = get_platform_client(LLMModel.OPENAI_GPT4o)

        system_prompt = await get_system_prompt(version=PromptVersion.V_2024_07_05)

        request_text = await PublicDataAPIService().response(publicDataApi.value)

        result = await ai_client.request(
            request_text=request_text,
            system_prompt=system_prompt,
            model=LLMModel.OPENAI_GPT4o,
        )

        ai_result = parse(result)

        return ai_result


# if __name__ == "__main__":
#     asyncio.run(PublicDataArticleService().public_data_to_article(PublicDataAPI.youth_policy))
