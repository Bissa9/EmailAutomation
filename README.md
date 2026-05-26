# Email Automation Bot

Python email automation bot for sending reports, reminders, bulk emails, and file attachments via **SMTP** or the **Gmail API**.

## Features

- **Single emails** — plain text, HTML, CC/BCC
- **Automated reports** — HTML templates with optional attachments
- **Reminders** — scheduled or one-off task reminders
- **Bulk email** — personalized sends from CSV or JSON recipient lists
- **File attachments** — attach one or more files automatically
- **Two providers** — Gmail SMTP (App Password) or Gmail API (OAuth2)
- **Scheduler** — daily automated reports and reminders
- **Docker support** — run the bot in containers via Docker Compose

## Project structure

```
EmailAuto/
├── main.py                 # CLI entry point
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Compose services (bot + scheduler)
├── config/settings.py      # Environment configuration
├── email_bot/
│   ├── smtp_client.py      # SMTP sender
│   ├── gmail_api.py        # Gmail API sender
│   ├── bulk_sender.py      # Bulk email logic
│   ├── scheduler.py        # Daily scheduling
│   ├── attachments.py      # File attachment handling
│   └── templates.py        # Jinja2 template rendering
├── templates/              # HTML email templates
├── data/                   # Sample recipient lists
├── attachments/            # Files to attach to emails
├── examples/               # Usage examples
└── credentials/            # Gmail API OAuth files (not committed)
```

## Setup

### 1. Install dependencies

```bash
cd EmailAuto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your Gmail address and credentials.

### Option A: SMTP (simplest)

1. Enable 2-Step Verification on your Google account
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Set in `.env`:

```
EMAIL_PROVIDER=smtp
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Option B: Gmail API (recommended for automation)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable the **Gmail API**
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` into `credentials/`
5. Set in `.env`:

```
EMAIL_PROVIDER=gmail_api
GMAIL_CREDENTIALS_PATH=credentials/credentials.json
GMAIL_TOKEN_PATH=credentials/token.json
```

On first run, a browser window opens for OAuth consent. The token is saved to `credentials/token.json`.

## Usage

### Send a single email with attachment

```bash
python main.py send \
  --to recipient@example.com \
  --subject "Hello" \
  --body "Please see the attached file." \
  --attach attachments/report.pdf
```

### Send a report

```bash
python main.py report \
  --to team@example.com \
  --title "Daily Sales Report" \
  --summary "Revenue up 8% today." \
  --attach attachments/report.pdf
```

### Send a reminder

```bash
python main.py reminder \
  --to user@example.com \
  --task "Submit timesheet" \
  --due "2026-05-30" \
  --notes "Due by end of day."
```

### Bulk email from CSV

Create a CSV with columns `email`, `name`, and any extra fields:

```csv
email,name,department
alice@example.com,Alice,Engineering
bob@example.com,Bob,Marketing
```

Send with personalization (`{name}`, `{department}` placeholders):

```bash
python main.py bulk \
  --recipients data/recipients.csv \
  --subject "Hello {name}" \
  --body "Hi {name}, update for {department} team."
```

Use `--html-file` for HTML bulk templates and `--delay 2` to pause between sends.

### Schedule daily automation

```bash
# Daily report at 9:00 AM
python main.py schedule \
  --type report \
  --time "09:00" \
  --to team@example.com \
  --title "Morning Report" \
  --summary "Automated daily summary."

# Daily reminder at 8:00 AM
python main.py schedule \
  --type reminder \
  --time "08:00" \
  --to user@example.com \
  --task "Stand-up meeting" \
  --due "Today 10:00 AM"
```

### Use Gmail API instead of SMTP

Add `--provider gmail_api` to any command:

```bash
python main.py send --provider gmail_api --to user@example.com --subject "Test" --body "Hello"
```

## Docker

Run the bot in a container with **Docker** and **Docker Compose**.

### Prerequisites

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make sure it is running.
2. Complete local setup first (`.env`, `credentials/credentials.json`).
3. **Authenticate on your Mac once** before using Docker — containers cannot open a browser for Google login:

```bash
python main.py send --to your-email@gmail.com --subject "Test" --body "Hello"
```

This creates `credentials/token.json`, which Docker mounts into the container.

### Build the image

```bash
docker compose build
```

### Send emails with Docker

```bash
docker compose run --rm email-bot send \
  --to your-email@gmail.com \
  --subject "Test from Docker" \
  --body "Email bot running in Docker"
```

### Other commands in Docker

**Report**
```bash
docker compose run --rm email-bot report \
  --to your-email@gmail.com \
  --title "Weekly Report" \
  --summary "Sent from Docker."
```

**Reminder**
```bash
docker compose run --rm email-bot reminder \
  --to your-email@gmail.com \
  --task "Submit report" \
  --due "2026-05-30"
```

**Bulk email**
```bash
docker compose run --rm email-bot bulk \
  --recipients data/recipients.csv \
  --subject "Hi {name}" \
  --body "Hello {name} from Docker."
```

**With attachment**
```bash
docker compose run --rm email-bot send \
  --to your-email@gmail.com \
  --subject "Report" \
  --body "See attached." \
  --attach attachments/report.pdf
```

### Run the scheduler in Docker

1. Edit the `scheduler` service in `docker-compose.yml` (time, recipient, title, etc.).
2. Start it in the background:

```bash
docker compose --profile scheduler up -d
```

3. View logs:

```bash
docker compose logs -f scheduler
```

4. Stop it:

```bash
docker compose --profile scheduler down
```

### What gets mounted

| Host path | Purpose |
|-----------|---------|
| `credentials/` | OAuth credentials + token |
| `.env` | Environment config (via `env_file`) |
| `data/` | CSV/JSON recipient lists |
| `attachments/` | Files to attach |
| `templates/` | HTML email templates |

Secrets are mounted from your machine and are **not** baked into the Docker image.

## Python API

```python
from pathlib import Path
from email_bot.base import EmailMessage
from email_bot.factory import create_email_client
from email_bot.bulk_sender import BulkEmailSender

client = create_email_client()  # or create_email_client("gmail_api")

message = EmailMessage(
    to=["user@example.com"],
    subject="Report",
    body="See attached.",
    attachments=[Path("attachments/report.pdf")],
)
client.send(message)

sender = BulkEmailSender(client, delay_seconds=1.0)
recipients = sender.load_recipients_from_csv(Path("data/recipients.csv"))
sender.send_bulk(
    recipients=recipients,
    subject_template="Hi {name}",
    body_template="Hello {name}, welcome!",
)
```

## Notes

- Gmail limits bulk sending (~500/day for regular accounts). Use `--delay` to avoid rate limits.
- Never commit `.env`, `credentials/credentials.json`, or `credentials/token.json` to version control.
- Place files to attach in the `attachments/` folder (create it as needed).
- For Docker + Gmail API: always generate `credentials/token.json` on your host before running containers.
