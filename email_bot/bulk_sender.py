from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path

from email_bot.base import EmailClient, EmailMessage, EmailResult


@dataclass
class BulkRecipient:
    email: str
    name: str = ""
    extra: dict | None = None


class BulkEmailSender:
    def __init__(self, client: EmailClient, delay_seconds: float = 1.0):
        self.client = client
        self.delay_seconds = delay_seconds

    @staticmethod
    def load_recipients_from_csv(path: Path) -> list[BulkRecipient]:
        recipients: list[BulkRecipient] = []
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                email = row.get("email", "").strip()
                if not email:
                    continue
                name = row.get("name", "").strip()
                extra = {k: v for k, v in row.items() if k not in {"email", "name"}}
                recipients.append(BulkRecipient(email=email, name=name, extra=extra))
        return recipients

    @staticmethod
    def load_recipients_from_json(path: Path) -> list[BulkRecipient]:
        data = json.loads(path.read_text(encoding="utf-8"))
        recipients: list[BulkRecipient] = []
        for item in data:
            email = item.get("email", "").strip()
            if not email:
                continue
            name = item.get("name", "").strip()
            extra = {k: v for k, v in item.items() if k not in {"email", "name"}}
            recipients.append(BulkRecipient(email=email, name=name, extra=extra))
        return recipients

    def send_bulk(
        self,
        recipients: list[BulkRecipient],
        subject_template: str,
        body_template: str,
        html_template: str | None = None,
        attachments: list[Path] | None = None,
        personalize: bool = True,
    ) -> list[EmailResult]:
        all_results: list[EmailResult] = []

        for index, recipient in enumerate(recipients):
            context = {
                "name": recipient.name or "there",
                "email": recipient.email,
                **(recipient.extra or {}),
            }

            subject = (
                subject_template.format(**context) if personalize else subject_template
            )
            body = body_template.format(**context) if personalize else body_template
            html_body = None
            if html_template:
                html_body = (
                    html_template.format(**context)
                    if personalize
                    else html_template
                )

            message = EmailMessage(
                to=[recipient.email],
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments or [],
            )
            results = self.client.send(message)
            all_results.extend(results)

            if index < len(recipients) - 1 and self.delay_seconds > 0:
                time.sleep(self.delay_seconds)

        return all_results
