from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_publisher import find_publisher
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.model.simplified_article import SimplifiedArticle
from app.model.subscription import MailTypeCategory
from app.rag_lang_chain.langchain_applied import request_rag_applied_openai
from app.service.article_manage_service import ArticleManageService
from app.service.crawl_article_service import CrawlArticleService
from app.utils.json_parser import parse


async def process_generate_article_by_url(
    url: str, publisher: str, session: AsyncSession
) -> SimplifiedArticle:
    # 프롬프트
    system_prompt = await get_system_prompt(version=PromptVersion.V_2024_07_14)

    # 크롤링한 기사
    request_text = await CrawlArticleService().crawl_article(
        url=url, news_type=publisher
    )

    system_prompt = system_prompt.format(original_text=request_text.content)

    # AI 번역 결과
    ai_result = await request_rag_applied_openai(request_text.content, system_prompt)
    ai_result = parse(ai_result.result_text)

    # Validate AI result
    if not ai_result.get("title") or not ai_result["title"].strip():
        raise ValueError("제목이 비어 있거나 누락되었습니다")
    if not ai_result.get("content") or not ai_result["content"].strip():
        raise ValueError("내용이 비어 있거나 누락되었습니다")
    if not ai_result.get("comment") or not ai_result["comment"].strip():
        raise ValueError("댓글이 비어 있거나 누락되었습니다")
    if ai_result.get("category") not in [
        category.name for category in MailTypeCategory
    ]:
        raise ValueError(f"유효하지 않은 카테고리입니다: {ai_result.get('category')}")

    # JSON 객체인 ai_result를 simplified_article 객체로 변환

    simplified_article = SimplifiedArticle(**ai_result)
    published_at_datetime = datetime.fromisoformat(request_text.pub_date).replace(
        tzinfo=None
    )
    # DB에 저장
    await ArticleManageService().create_article(
        url=url,
        publisher=find_publisher(publisher),
        title=request_text.title,
        content=request_text.content,
        simple_title=simplified_article.title,
        simple_content=simplified_article.content,
        phrase=simplified_article.phrase,
        comment=simplified_article.comment,
        published_at=published_at_datetime,
        image_url=request_text.image_url,
        category=MailTypeCategory(ai_result["category"]),
        session=session,
    )

    return simplified_article
