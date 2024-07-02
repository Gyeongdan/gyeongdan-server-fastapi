from sqlalchemy.ext.asyncio import AsyncSession

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.article_publisher import find_publisher
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.service.article_manage_service import ArticleManageService
from app.service.crawl_article_service import CrawlArticleService
from app.utils.json_parser import parse


async def generate_simple_article(url: str, publisher: str, session: AsyncSession):
    ai_client = get_platform_client(LLMModel.GROQ_LLAMA_3)

    # 프롬프트
    system_prompt = await get_system_prompt(version=PromptVersion.V_2024_07_02)

    # 크롤링한 기사
    request_text = await CrawlArticleService().crawl_article(
        url=url, news_type=publisher
    )

    # AI 요청
    ai_result = parse(
        await ai_client.request(
            request_text=request_text.content,
            system_prompt=system_prompt,
            assistant_prompt=None,
            model=LLMModel.GROQ_LLAMA_3,
        )
    )

    await ArticleManageService().create_article(
        url=url,
        publisher=find_publisher(publisher),
        title=request_text.title,
        content=request_text.content,
        simple_title=ai_result["title"],
        simple_content=ai_result["content"],
        session=session,
    )

    return ai_result
