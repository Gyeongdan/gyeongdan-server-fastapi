from sqlalchemy.ext.asyncio import AsyncSession

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.service.crawl_article_service import CrawlArticleService


async def generate_simple_article(url: str, publisher: str, session: AsyncSession):
    ai_client = get_platform_client(LLMModel.GROQ_LLAMA_3)
    system_prompt = (
        f"대한민국의 20대 초반이 읽기 쉬울 수준으로 쉬운 기사로 재생성 해줘: {url}"
    )
    assistant_prompt = ""

    request_text = await CrawlArticleService().crawl_article(
        url=url, news_type=publisher, session=session
    )

    return await ai_client.request(
        request_text=request_text.content,
        system_prompt=system_prompt,
        assistant_prompt=[assistant_prompt],
        model=LLMModel.GROQ_LLAMA_3,
    )
