import json
import ssl
from datetime import datetime
from typing import List

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.model.article_model import ArticleResponse
from app.model.article_publisher import Publisher, find_publisher


class CrawlArticleService:
    def __init__(self):
        self.__find_image_dict = {
            Publisher.HAN_KYUNG.name: self.__find_image_han_kyung,
            Publisher.MAE_KYUNG.name: self.__find_image_mae_kyung,
            Publisher.SEOUL_KYUNG.name: self.__find_image_seoul_kyung
        }


    async def crawl_article(self, news_type: str, url: str) -> ArticleResponse:
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
        pub_date = self.__find_pub_date(result_html, news_type)
        image_url = self.__find_image(result_html, news_type)
        if news_type == Publisher.SEOUL_KYUNG:
            content = self.__find_content_from_script(result_html)
        else:
            main_section = self.__find_main_section(result_html, news_type)
            content = self.__find_content_from_main_section(main_section, news_type)

        if not content.strip():
            raise HTTPException(status_code=404, detail="파싱 결과가 없습니다.")

        return ArticleResponse(title=title, content=content, pub_date=pub_date, image_url=image_url)

    async def __fetch_page(self, url: str) -> str:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with ClientSession() as session:
            async with session.get(url, ssl=ssl_context) as response:
                return await response.text()


    def __find_image(self, soup: BeautifulSoup, news_type: Publisher):
        return self.__find_image_dict[news_type.name](soup)


    def __find_pub_date(self, soup: BeautifulSoup, news_type: Publisher):
        property_str = ''
        if news_type == Publisher.HAN_KYUNG:
            property_str = 'article:published'
        else:
            property_str = "article:published_time"
        pub_date_element = soup.find("meta", property=property_str)
        pub_date = pub_date_element["content"] if pub_date_element else "pub date not found"

        if news_type == Publisher.HAN_KYUNG:
            date_obj = datetime.fromisoformat(pub_date)
            pub_date = date_obj.isoformat()
        return pub_date

    def __find_title(self, soup: BeautifulSoup, news_type: Publisher) -> str:
        if news_type == Publisher.SEOUL_KYUNG:
            title_element = soup.find("meta", property="og:title")
            title = title_element["content"] if title_element else "Title not found"
        else:
            title_element = soup.find(
                news_type.value.title_tag, class_=news_type.value.title_class
            )
            title = (
                title_element.get_text(strip=True)
                if title_element
                else "Title not found"
            )
        return title

    def __find_main_section(self, result_html: BeautifulSoup, news_type: Publisher):
        main_section = result_html.find("div", class_=news_type.value.content_div_class)
        if not main_section:
            raise HTTPException(
                status_code=404, detail="Main content section not found"
            )
        return main_section

    def __find_content_from_main_section(
        self, main_section: BeautifulSoup, news_type: Publisher
    ) -> str:
        paragraphs = [
            para
            for tag in news_type.value.content_tags
            for para in main_section.find_all(tag, recursive=False)
        ]

        content = []
        for para in paragraphs:
            if para.name == "p":
                text = para.get_text(strip=True)
                content.append(text)
            elif para.name == "br":
                if para.previous_sibling and isinstance(para.previous_sibling, str):
                    content.append(para.previous_sibling.strip())

        return "\n".join(content)

    def __find_content_from_script(self, result_html: BeautifulSoup) -> str:
        script_tag = result_html.find("script", type="application/ld+json")
        if not script_tag:
            raise HTTPException(status_code=404, detail="Content script not found")

        script_content = script_tag.string
        json_content = json.loads(script_content)
        article_body = json_content.get("articleBody", "")

        return article_body

    def __find_image_han_kyung(soup: BeautifulSoup):
        figure_img_div = soup.find('div', class_='figure-img')

        # figure-img 클래스를 가진 div 태그가 있다면
        if figure_img_div:
            # 그 안의 img 태그 선택
            img_tag = figure_img_div.find('img')
            if img_tag:
                img_url = img_tag.get('src')
                return img_url

    def __find_image_mae_kyung(soup: BeautifulSoup):
        thumb_div = soup.find('div', class_='thumb_area img')
        if thumb_div:
            # 그 안의 img 태그 선택
            img_tag = thumb_div.find('img')
            if img_tag:
                img_url = img_tag.get('src')
                return img_url

    def __find_image_seoul_kyung(soup: BeautifulSoup):
        photo_span = soup.find('span', class_='photo')

        # photo 클래스를 가진 span 태그가 있다면
        if photo_span:
            # 그 안의 img 태그 선택
            img_tag = photo_span.find('img')
            if img_tag:
                img_url = img_tag.get('src')
                return img_url