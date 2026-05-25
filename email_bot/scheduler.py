from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import schedule

from email_bot.base import EmailClient, EmailMessage
from email_bot.templates import render_reminder_email, render_report_email


class EmailScheduler:
    def __init__(self, client: EmailClient):
        self.client = client
        self._jobs = schedule.Scheduler()

    def schedule_daily_report(
        self,
        time_str: str,
        recipients: list[str],
        report_title: str,
        report_summary: str,
        attachments: list[Path] | None = None,
    ) -> None:
        def job():
            report_date = datetime.now().strftime("%Y-%m-%d")
            for recipient in recipients:
                subject, html_body = render_report_email(
                    recipient_name=recipient.split("@")[0],
                    report_title=report_title,
                    report_summary=report_summary,
                    report_date=report_date,
                )
                message = EmailMessage(
                    to=[recipient],
                    subject=subject,
                    body=report_summary,
                    html_body=html_body,
                    attachments=attachments or [],
                )
                self.client.send(message)

        self._jobs.every().day.at(time_str).do(job)

    def schedule_reminder(
        self,
        time_str: str,
        recipient: str,
        task_title: str,
        due_date: str,
        notes: str = "",
    ) -> None:
        def job():
            subject, html_body = render_reminder_email(
                recipient_name=recipient.split("@")[0],
                task_title=task_title,
                due_date=due_date,
                notes=notes,
            )
            message = EmailMessage(
                to=[recipient],
                subject=subject,
                body=f"Reminder: {task_title} is due on {due_date}. {notes}",
                html_body=html_body,
            )
            self.client.send(message)

        self._jobs.every().day.at(time_str).do(job)

    def run_pending(self) -> None:
        self._jobs.run_pending()

    def run_forever(self, poll_interval: int = 60) -> None:
        print("Scheduler running. Press Ctrl+C to stop.")
        while True:
            self.run_pending()
            time.sleep(poll_interval)
