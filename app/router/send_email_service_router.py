# send_email_service_router.py

from datetime import datetime, timedelta
from enum import Enum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.model.subscription import MailTypeCategory
from app.service.newsletter_article_service import NewsletterService
from app.service.send_email_service import SendEmailService
from app.service.subscription_service import SubscriptionService


class TimeDelta(Enum):
    # 12 시간 안에 신규 기사만 선정
    RECENT_HOURS = 12


send_email_service_router = APIRouter()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@email.com"  # 예시입니다!
SMTP_PASSWORD = "PASSWORD_PLEASE"  # 예시입니다!

sender = SendEmailService(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)


@send_email_service_router.post("/send-email/")
async def send_email(
    category: MailTypeCategory, session: AsyncSession = Depends(get_db_session)
):
    # email_list 받아오기
    subscriptions = await SubscriptionService().get_active_subcriptions_by_category(
        category, session
    )
    email_list = [subscription.email_address for subscription in subscriptions]

    # news_letter 받아오기
    time_now = datetime.now()
    news_letters = await NewsletterService().get_content_by_category(category, session)
    letter_list = [
        news_letter.content
        for news_letter in news_letters
        # 기준을 12시간 안에 기사가 생성됐냐 안됐냐로 따졌습니다. 이는 조정하면 될 것 같습니다!
        if news_letter.updated_at
        >= (time_now - timedelta(hours=TimeDelta.RECENT_HOURS.value))
    ]

    # email 누가 받았는 지 체크
    for article in letter_list:
        repository = await NewsletterService().get_id_by_content(article, session)
        for email in email_list:
            await NewsletterService().update_email(repository, email, session)

    news_article_zip = "\n\n".join(letter_list)

    # user들 한테 email 보내는 것!
    # return 은 바뀌어도 됩니다!
    await sender.send_email_to_users(category.value, news_article_zip, email_list)
    return letter_list
