from fastapi import HTTPException

import requests
from bs4 import BeautifulSoup

from app.model.article_model import ArticleResponse


async def extract_article(url: str):
    # 웹 페이지 가져오기
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청이 성공하지 않으면 예외 발생
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching the URL: {str(e)}")

    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_element = soup.find('h2', class_='news_ttl')
    if title_element:
        title = title_element.get_text(strip=True)
    else:
        title = "Title not found"

    # 내용 추출
    main_section = soup.find('div', class_='news_cnt_detail_wrap')
    if not main_section:
        raise HTTPException(status_code=404, detail="Main content section not found")

    # refid가 있는 모든 p 태그를 찾습니다
    paragraphs = main_section.find_all('p', attrs={'refid': True})
    if not paragraphs:
        raise HTTPException(status_code=404, detail="No paragraphs with refid found")

    # 텍스트를 저장할 리스트
    content = []
    for para in paragraphs:
        if para.get('refid') and para.name == 'p':
            text = para.get_text(strip=True)
            content.append(text)

    # 텍스트를 하나의 문자열로 합치기
    full_content = "\n".join(content)

    return ArticleResponse(title=title, content=full_content)

