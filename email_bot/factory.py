from __future__ import annotations

from config.settings import EMAIL_PROVIDER
from email_bot.base import EmailClient
from email_bot.gmail_api import GmailAPIClient
from email_bot.smtp_client import SMTPEmailClient


def create_email_client(provider: str | None = None) -> EmailClient:
    selected = (provider or EMAIL_PROVIDER).lower()

    if selected == "gmail_api":
        return GmailAPIClient()
    if selected == "smtp":
        return SMTPEmailClient()

    raise ValueError(f"Unknown email provider: {selected}. Use 'smtp' or 'gmail_api'.")
