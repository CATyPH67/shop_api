from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config.settings_config import settings
from pydantic import EmailStr
from app.config.logging_config import logger


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
        recipients=[to],
        body=html_content,
        subtype="html",
    )
    fm = FastMail(conf)

    try:
        logger.info(
            "Sending email",
            extra={"extra_fields": {"to": str(to)}}
        )
        await fm.send_message(message)
        logger.info(
            "Email sent successfully",
            extra={"extra_fields": {"to": str(to)}}
        )
    except Exception as e:
        logger.exception(
            "Failed to send email",
            extra={"extra_fields": {"to": str(to)}}
        )
        raise e