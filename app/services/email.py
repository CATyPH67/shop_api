from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings
from pydantic import EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False
)


async def send_email(to: EmailStr, subject: str, html_content: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],  # список email
        body=html_content,
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
