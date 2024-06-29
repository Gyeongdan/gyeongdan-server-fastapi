# send_email_service_router.py
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# 활용을 위하여
from app.database.session import get_db_session

# 내가 만든 db 가져오기
from app.service.newsletter_article_service import NewsletterService

# 윤성이가 만든 emailservice
from app.service.send_email_service import SendEmailService

# 윤성이가 만든 subscription db 가져오기
from app.service.subscription_service import SubscriptionService

send_email_service_router = APIRouter()

# email을 string으로 받을 지 email로 받을 지
# category는 Enum으로 바꿔야 할 듯


class SendEmailContent(BaseModel):
    category: int
    contents: List[str]
    email: List[str]


# 우선 내껄로 테스트
sender = SendEmailService(
    "smtp.gmail.com", 587, "jys0972@gmail.com", "ktoc hgtz fzpm mbcg"
)


@send_email_service_router.post("/send-email/")
async def send_email(category: int, session: AsyncSession = Depends(get_db_session)):
    # email_list 받아오기
    subscriptions = await SubscriptionService().get_active_subcriptions_by_category(
        category, session
    )
    email_list = [subscription.email_address for subscription in subscriptions]
    print(email_list)

    # news_letter 받아오기
    # 시간 기준은 함수 실행
    time_now = datetime.now()
    news_letters = await NewsletterService().get_content_by_category(category, session)
    letter_list = [
        news_letter.content
        for news_letter in news_letters
        if news_letter.updated_at >= (time_now - timedelta(hours=12))
    ]
    return letter_list
