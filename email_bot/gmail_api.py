import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.settings import (
    DEFAULT_FROM_EMAIL,
    DEFAULT_FROM_NAME,
    GMAIL_CREDENTIALS_PATH,
    GMAIL_TOKEN_PATH,
)
from email_bot.attachments import attach_files
from email_bot.base import EmailMessage, EmailResult

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class GmailAPIClient:
    def __init__(
        self,
        credentials_path: Path = GMAIL_CREDENTIALS_PATH,
        token_path: Path = GMAIL_TOKEN_PATH,
    ):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service

        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Download OAuth credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(creds.to_json())

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def send(self, message: EmailMessage) -> list[EmailResult]:
        service = self._get_service()
        from_email = message.from_email or DEFAULT_FROM_EMAIL
        from_name = message.from_name or DEFAULT_FROM_NAME

        results: list[EmailResult] = []
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

                raw = base64.urlsafe_b64encode(mime.as_bytes()).decode("utf-8")
                service.users().messages().send(
                    userId="me", body={"raw": raw}
                ).execute()

                results.append(EmailResult(success=True, recipient=recipient))
            except Exception as exc:
                results.append(
                    EmailResult(success=False, recipient=recipient, error=str(exc))
                )

        return results
