from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class EmailMessage:
    to: list[str]
    subject: str
    body: str
    html_body: str | None = None
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    attachments: list[Path] = field(default_factory=list)
    from_email: str | None = None
    from_name: str | None = None


@dataclass
class EmailResult:
    success: bool
    recipient: str
    error: str | None = None


class EmailClient(Protocol):
    def send(self, message: EmailMessage) -> list[EmailResult]:
        ...
