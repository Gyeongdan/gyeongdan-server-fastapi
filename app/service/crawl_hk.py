from fastapi import HTTPException
import requests
from bs4 import BeautifulSoup
from app.model.article_model import ArticleResponse

async def extract_article_hk(url: str) -> ArticleResponse:
    # 웹 페이지 가져오기
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching the URL: {str(e)}")

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_element = soup.find('h1', class_='headline')
    if title_element:
        title = title_element.get_text(strip=True)
    else:
        title = "Title not found"

    # 본문 추출
    main_section = soup.find('div', class_='article-body')
    if not main_section:
        print(f"Main content section not found for URL: {url}")
        raise HTTPException(status_code=404, detail="Main content section not found")

    content = []
    paragraphs = main_section.find_all(['p', 'br'])

    # 이전 형제 텍스트를 포함해 텍스트를 추출
    for para in paragraphs:
        text = para.previous_sibling
        if text and isinstance(text, str):
            content.append(text.strip())

    full_content = "\n".join(content).strip()

    if not full_content:
        print(f"No content found for URL: {url}")
        raise HTTPException(status_code=404, detail="No content found")

    return ArticleResponse(title=title, content=full_content)
