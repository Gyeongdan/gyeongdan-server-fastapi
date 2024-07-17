from langchain.schema import Document
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_publisher import find_publisher
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.model.simplified_article import SimplifiedArticle
from app.model.subscription import MailTypeCategory
from app.rag_lang_chain.langchain_applied import request_rag_applied_openai
from app.service.article_manage_service import ArticleManageService
from app.service.crawl_article_service import CrawlArticleService
from app.utils.json_parser import parse
from app.service.article_related_document_service import ArticleRelatedDocumentService

async def process_generate_article_by_url(
    url: str, publisher: str, session: AsyncSession
) -> SimplifiedArticle:
    # 프롬프트
    system_prompt = await get_system_prompt(version=PromptVersion.V_2024_07_14)

    # 크롤링한 기사
    request_text = await CrawlArticleService().crawl_article(
        url=url, news_type=publisher
    )

    # 프롬프트 + 크롤링한 기사 원문
    system_prompt = system_prompt.format(original_text=request_text.content)

    # Rang Chain을 이용한 AI 번역 결과
    ai_result = await request_rag_applied_openai(request_text.content, system_prompt)
    ai_result_text = parse(ai_result.result_text)

    # Validate AI result
    if not ai_result_text.get("title") or not ai_result_text["title"].strip():
        raise ValueError("제목이 비어 있거나 누락되었습니다")
    if not ai_result_text.get("content") or not ai_result_text["content"].strip():
        raise ValueError("내용이 비어 있거나 누락되었습니다")
    if not ai_result_text.get("comment") or not ai_result_text["comment"].strip():
        raise ValueError("댓글이 비어 있거나 누락되었습니다")
    if ai_result_text.get("category") not in [
        category.value for category in MailTypeCategory
    ]:
        raise ValueError(f"유효하지 않은 카테고리입니다: {ai_result_text.get('category')}")

    ### 크롤링한 기사를 DB에 저장
    # JSON 객체인 ai_result를 simplified_article 객체로 변환
    simplified_article = SimplifiedArticle(**ai_result_text)
    # DB에 저장
    article = await ArticleManageService().create_article(url=url, publisher=find_publisher(publisher),
                                                           title=request_text.title, content=request_text.content,
                                                           simple_title=simplified_article.title,
                                                           simple_content=simplified_article.content,
                                                           phrase=simplified_article.phrase,
                                                           comment=simplified_article.comment,
                                                           published_at=request_text.pub_date,
                                                           image_url=request_text.image_url,
                                                           category=MailTypeCategory(ai_result_text["category"]),
                                                           session=session, )


    ### 크롤링한 기사에 관련된 문서들을 DB에 저장
    # JSON 객체인 ai_result.related_documents를 realated_documents 객체로 변환 및 저장
    related_documents_lst = ai_result.related_documents
    # DB에 저장
    # DB에 저장
    for doc in related_documents_lst:
        related_document = {
            "title": doc.metadata.get("title", "제목 없음"),
            "link": doc.metadata.get("source", "URL 없음"),
            "snippet": doc.page_content
        } if isinstance(doc, Document) else doc

        await ArticleRelatedDocumentService().save(article.id, related_document, session)

    return simplified_article
