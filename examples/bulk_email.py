"""Example: send bulk personalized emails from CSV."""

from pathlib import Path

from email_bot.bulk_sender import BulkEmailSender
from email_bot.factory import create_email_client


def main() -> None:
    client = create_email_client()
    sender = BulkEmailSender(client, delay_seconds=1.0)

    recipients = sender.load_recipients_from_csv(Path("data/recipients.csv"))

    results = sender.send_bulk(
        recipients=recipients,
        subject_template="Hello {name} — update from {department}",
        body_template=(
            "Hi {name},\n\n"
            "This is a bulk update for the {department} team.\n\n"
            "Regards,\nEmail Bot"
        ),
        html_template=(
            "<p>Hi <strong>{name}</strong>,</p>"
            "<p>This is a bulk update for the <em>{department}</em> team.</p>"
        ),
    )

    success = sum(1 for r in results if r.success)
    print(f"Sent {success}/{len(results)} emails")


if __name__ == "__main__":
    main()
