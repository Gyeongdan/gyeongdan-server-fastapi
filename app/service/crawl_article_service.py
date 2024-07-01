import ssl

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.model.article_model import ArticleResponse
from app.model.article_publisher import Publisher, find_publisher


class CrawlArticleService:

    async def crawl_article(self, news_type: str, url: str) -> ArticleResponse:
        print(f"news_type: {news_type}, url: {url}")
        news_type = find_publisher(news_type)

        # 웹 페이지 가져오기
        try:
            response_text = await self.__fetch_page(url)
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=400, detail=f"Error fetching the URL: {str(e)}"
            ) from e

        result_html = BeautifulSoup(response_text, "html.parser")
        title = self.__find_title(result_html, news_type)
        main_section = self.__find_main_section(result_html, news_type)
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

        return ArticleResponse(title=title, content=full_content)

    async def __fetch_page(self, url: str) -> str:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with ClientSession() as session:
            async with session.get(url, ssl=ssl_context) as response:
                return await response.text()

    def __find_title(self, soup: BeautifulSoup, news_type: Publisher) -> str:
        title_element = soup.find(
            news_type.value.title_tag, class_=news_type.value.title_class
        )
        title = (
            title_element.get_text(strip=True) if title_element else "Title not found"
        )

        return title

    def __find_main_section(self, result_html: BeautifulSoup, news_type: Publisher):
        main_section = result_html.find("div", class_=news_type.value.content_div_class)
        if not main_section:
            raise HTTPException(
                status_code=404, detail="Main content section not found"
            )
        return main_section
