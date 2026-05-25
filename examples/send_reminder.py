"""Example: send a reminder email."""

from email_bot.base import EmailMessage
from email_bot.factory import create_email_client
from email_bot.templates import render_reminder_email


def main() -> None:
    client = create_email_client()
    recipient = "recipient@example.com"

    subject, html_body = render_reminder_email(
        recipient_name="Alex",
        task_title="Submit quarterly review",
        due_date="2026-05-30",
        notes="Please upload the document to the shared drive.",
    )

    message = EmailMessage(
        to=[recipient],
        subject=subject,
        body="Reminder: Submit quarterly review is due on 2026-05-30.",
        html_body=html_body,
    )

    results = client.send(message)
    for result in results:
        print(f"{'Sent' if result.success else 'Failed'}: {result.recipient}")


if __name__ == "__main__":
    main()
