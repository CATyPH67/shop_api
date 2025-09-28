from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config.smtp_config import connection_config
from pydantic import EmailStr
from app.config.logging_config import logger


async def send_email(to: EmailStr, subject: str, html_content: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=html_content,
        subtype="html",
    )
    fm = FastMail(connection_config)

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