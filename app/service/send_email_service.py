from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import aiosmtplib


class SendEmailService:
    def __init__(
        self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    async def send_email_to_user(self, subject: str, body: str, user: str):
        message = MIMEMultipart()
        message["From"] = self.smtp_user
        message["To"] = user
        message["Subject"] = subject

        body_part = MIMEText(body, "plain")
        message.attach(body_part)

        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            start_tls=True,
        )

    async def send_email_to_users(self, subject: str, body: str, users: List[str]):
        for user in users:
            await self.send_email_to_user(subject, body, user)
