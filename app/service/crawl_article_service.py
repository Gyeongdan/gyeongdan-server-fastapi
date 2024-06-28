import ssl

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_model import ArticleResponse
from app.model.article_publisher import Publisher, find_publisher
from app.service.crawled_article_service import ArticleService


async def fetch_page(url: str) -> str:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as response:
            return await response.text()


async def extract_article(
    news_type: str, url: str, session: AsyncSession
) -> ArticleResponse:
    news_type = find_publisher(news_type)

    # 웹 페이지 가져오기
    try:
        response_text = await fetch_page(url)
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=400, detail=f"Error fetching the URL: {str(e)}"
        ) from e

    result_html = BeautifulSoup(response_text, "html.parser")
    title = find_title(result_html, news_type)
    main_section = find_main_section(result_html, news_type)
    paragraphs = [
        para
        for tag in news_type.value.content_tags
        for para in main_section.find_all(tag, attrs=news_type.value.content_attrs)
    ]

    content = []
    if news_type == Publisher.MAE_KYUNG:
        for para in paragraphs:
            if para.get("refid") and para.name == "p":
                text = para.get_text(strip=True)
                content.append(text)
    elif news_type in {Publisher.HAN_KYUNG, Publisher.SEOUL_KYUNG}:
        for para in paragraphs:
            if para.name == "p":
                content.append(para.get_text(strip=True))
            elif para.name == "br":
                text = para.previous_sibling
                if text and isinstance(text, str):
                    content.append(text.strip())

    full_content = "\n".join(content)

    if not full_content.strip():
        raise HTTPException(status_code=404, detail="파싱 결과가 없습니다.")

    await save_article_to_db(url, news_type, title, full_content, session)
    return ArticleResponse(title=title, content=full_content)


def find_title(soup: BeautifulSoup, news_type: Publisher) -> str:
    title_element = soup.find(
        news_type.value.title_tag, class_=news_type.value.title_class
    )
    title = title_element.get_text(strip=True) if title_element else "Title not found"

    return title


def find_main_section(result_html: BeautifulSoup, news_type: Publisher):
    main_section = result_html.find("div", class_=news_type.value.content_div_class)
    if not main_section:
        raise HTTPException(status_code=404, detail="Main content section not found")
    return main_section


async def save_article_to_db(
    url: str, publisher: Publisher, title: str, content: str, session: AsyncSession
):
    return await ArticleService().create_article(
        url=url, publisher=publisher, title=title, content=content, session=session
    )
