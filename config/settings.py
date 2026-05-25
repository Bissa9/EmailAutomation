import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp").lower()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

GMAIL_CREDENTIALS_PATH = BASE_DIR / os.getenv(
    "GMAIL_CREDENTIALS_PATH", "credentials/credentials.json"
)
GMAIL_TOKEN_PATH = BASE_DIR / os.getenv("GMAIL_TOKEN_PATH", "credentials/token.json")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", SMTP_USER)
DEFAULT_FROM_NAME = os.getenv("DEFAULT_FROM_NAME", "Email Automation Bot")

TEMPLATES_DIR = BASE_DIR / "templates"
ATTACHMENTS_DIR = BASE_DIR / "attachments"
DATA_DIR = BASE_DIR / "data"
