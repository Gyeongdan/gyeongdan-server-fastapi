from fastapi import HTTPException
import aiohttp
from bs4 import BeautifulSoup
from app.model.article_model import ArticleResponse, news_settings

async def fetch_page(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=400, detail=f"Error fetching the URL: {response.status}")
            return await response.text()

async def extract_article(news_type: str, url: str) -> ArticleResponse:
    if news_type not in news_settings:
        raise HTTPException(status_code=400, detail=f"Invalid news type: {news_type}")

    settings = news_settings[news_type]

    # 웹 페이지 가져오기
    try:
        response_text = await fetch_page(url)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=400, detail=f"Error fetching the URL: {str(e)}")

    # HTML 파싱
    soup = BeautifulSoup(response_text, 'html.parser')

    # 제목 추출
    title_element = soup.find(settings["title_tag"], class_=settings["title_class"])
    title = title_element.get_text(strip=True) if title_element else "Title not found"

    # 본문 추출
    main_section = soup.find('div', class_=settings["content_div_class"])
    if not main_section:
        raise HTTPException(status_code=404, detail="Main content section not found")

    paragraphs = []
    for tag in settings["content_tags"]:
        paragraphs.extend(main_section.find_all(tag, attrs=settings["content_attrs"]))

    if not paragraphs:
        raise HTTPException(status_code=404, detail="No content found")

    content = []
    if news_type == "MAE_KYUNG":
        for para in paragraphs:
            if para.get('refid') and para.name == 'p':
                text = para.get_text(strip=True)
                content.append(text)
    elif news_type == "HAN_KYUNG" or news_type == "SEOUL_KUNG":
        for para in paragraphs:
            if para.name == 'p':
                content.append(para.get_text(strip=True))
            elif para.name == 'br':
                text = para.previous_sibling
                if text and isinstance(text, str):
                    content.append(text.strip())

    full_content = "\n".join(content)

    if not full_content.strip():
        raise HTTPException(status_code=404, detail="No content found")

    return ArticleResponse(title=title, content=full_content)
