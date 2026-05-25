"""Example: send a report email with attachment."""

from datetime import datetime
from pathlib import Path

from email_bot.base import EmailMessage
from email_bot.factory import create_email_client
from email_bot.templates import render_report_email


def main() -> None:
    client = create_email_client()
    recipient = "recipient@example.com"

    subject, html_body = render_report_email(
        recipient_name="Team",
        report_title="Weekly Sales Report",
        report_summary="Total sales increased by 12% this week.",
        report_date=datetime.now().strftime("%Y-%m-%d"),
    )

    attachments = []
    report_file = Path("attachments/sample_report.pdf")
    if report_file.exists():
        attachments.append(report_file)

    message = EmailMessage(
        to=[recipient],
        subject=subject,
        body="Weekly sales report attached.",
        html_body=html_body,
        attachments=attachments,
    )

    results = client.send(message)
    for result in results:
        print(f"{'Sent' if result.success else 'Failed'}: {result.recipient}")


if __name__ == "__main__":
    main()
