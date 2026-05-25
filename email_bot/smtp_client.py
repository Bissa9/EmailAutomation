import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from config.settings import (
    DEFAULT_FROM_EMAIL,
    DEFAULT_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)
from email_bot.attachments import attach_files
from email_bot.base import EmailMessage, EmailResult


class SMTPEmailClient:
    def __init__(
        self,
        host: str = SMTP_HOST,
        port: int = SMTP_PORT,
        user: str = SMTP_USER,
        password: str = SMTP_PASSWORD,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send(self, message: EmailMessage) -> list[EmailResult]:
        if not self.user or not self.password:
            raise ValueError(
                "SMTP_USER and SMTP_PASSWORD must be set in .env"
            )

        results: list[EmailResult] = []
        from_email = message.from_email or DEFAULT_FROM_EMAIL
        from_name = message.from_name or DEFAULT_FROM_NAME

        for recipient in message.to:
            try:
                mime = MIMEMultipart("mixed")
                mime["From"] = formataddr((from_name, from_email))
                mime["To"] = recipient
                mime["Subject"] = message.subject

                if message.cc:
                    mime["Cc"] = ", ".join(message.cc)
                if message.bcc:
                    mime["Bcc"] = ", ".join(message.bcc)

                alternative = MIMEMultipart("alternative")
                alternative.attach(MIMEText(message.body, "plain", "utf-8"))
                if message.html_body:
                    alternative.attach(MIMEText(message.html_body, "html", "utf-8"))
                mime.attach(alternative)

                if message.attachments:
                    attach_files(mime, message.attachments)

                all_recipients = [recipient, *message.cc, *message.bcc]
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.user, self.password)
                    server.sendmail(from_email, all_recipients, mime.as_string())

                results.append(EmailResult(success=True, recipient=recipient))
            except Exception as exc:
                results.append(
                    EmailResult(success=False, recipient=recipient, error=str(exc))
                )

        return results
