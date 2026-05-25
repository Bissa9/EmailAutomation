#!/usr/bin/env python3
"""CLI for the Email Automation Bot."""

import argparse
from datetime import datetime
from pathlib import Path

from email_bot.base import EmailMessage
from email_bot.bulk_sender import BulkEmailSender
from email_bot.factory import create_email_client
from email_bot.scheduler import EmailScheduler
from email_bot.templates import render_reminder_email, render_report_email


def cmd_send(args: argparse.Namespace) -> None:
    client = create_email_client(args.provider)
    attachments = [Path(p) for p in args.attach or []]

    message = EmailMessage(
        to=args.to,
        subject=args.subject,
        body=args.body,
        html_body=args.html,
        cc=args.cc or [],
        bcc=args.bcc or [],
        attachments=attachments,
    )
    results = client.send(message)
    _print_results(results)


def cmd_report(args: argparse.Namespace) -> None:
    client = create_email_client(args.provider)
    attachments = [Path(p) for p in args.attach or []]
    report_date = args.date or datetime.now().strftime("%Y-%m-%d")

    for recipient in args.to:
        subject, html_body = render_report_email(
            recipient_name=recipient.split("@")[0],
            report_title=args.title,
            report_summary=args.summary,
            report_date=report_date,
        )
        message = EmailMessage(
            to=[recipient],
            subject=subject,
            body=args.summary,
            html_body=html_body,
            attachments=attachments,
        )
        results = client.send(message)
        _print_results(results)


def cmd_reminder(args: argparse.Namespace) -> None:
    client = create_email_client(args.provider)

    for recipient in args.to:
        subject, html_body = render_reminder_email(
            recipient_name=recipient.split("@")[0],
            task_title=args.task,
            due_date=args.due,
            notes=args.notes or "",
        )
        message = EmailMessage(
            to=[recipient],
            subject=subject,
            body=f"Reminder: {args.task} is due on {args.due}. {args.notes or ''}",
            html_body=html_body,
        )
        results = client.send(message)
        _print_results(results)


def cmd_bulk(args: argparse.Namespace) -> None:
    client = create_email_client(args.provider)
    sender = BulkEmailSender(client, delay_seconds=args.delay)
    source = Path(args.recipients)

    if source.suffix.lower() == ".csv":
        recipients = sender.load_recipients_from_csv(source)
    elif source.suffix.lower() == ".json":
        recipients = sender.load_recipients_from_json(source)
    else:
        raise ValueError("Recipients file must be .csv or .json")

    attachments = [Path(p) for p in args.attach or []]
    html_template = None
    if args.html_file:
        html_template = Path(args.html_file).read_text(encoding="utf-8")

    results = sender.send_bulk(
        recipients=recipients,
        subject_template=args.subject,
        body_template=args.body,
        html_template=html_template,
        attachments=attachments,
    )
    _print_results(results)


def cmd_schedule(args: argparse.Namespace) -> None:
    client = create_email_client(args.provider)
    scheduler = EmailScheduler(client)
    attachments = [Path(p) for p in args.attach or []]

    if args.type == "report":
        scheduler.schedule_daily_report(
            time_str=args.time,
            recipients=args.to,
            report_title=args.title,
            report_summary=args.summary,
            attachments=attachments,
        )
    else:
        scheduler.schedule_reminder(
            time_str=args.time,
            recipient=args.to[0],
            task_title=args.task,
            due_date=args.due,
            notes=args.notes or "",
        )

    print(f"Scheduled daily {args.type} at {args.time}. Starting scheduler...")
    scheduler.run_forever()


def _print_results(results) -> None:
    for result in results:
        if result.success:
            print(f"✓ Sent to {result.recipient}")
        else:
            print(f"✗ Failed for {result.recipient}: {result.error}")


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--provider",
        choices=["smtp", "gmail_api"],
        default=None,
        help="Email provider (default from .env)",
    )

    parser = argparse.ArgumentParser(description="Email Automation Bot")
    sub = parser.add_subparsers(dest="command", required=True)

    send = sub.add_parser("send", parents=[parent], help="Send a single email")
    send.add_argument("--to", nargs="+", required=True)
    send.add_argument("--subject", required=True)
    send.add_argument("--body", required=True)
    send.add_argument("--html")
    send.add_argument("--cc", nargs="*")
    send.add_argument("--bcc", nargs="*")
    send.add_argument("--attach", nargs="*", help="File paths to attach")
    send.set_defaults(func=cmd_send)

    report = sub.add_parser("report", parents=[parent], help="Send a report email")
    report.add_argument("--to", nargs="+", required=True)
    report.add_argument("--title", required=True)
    report.add_argument("--summary", required=True)
    report.add_argument("--date")
    report.add_argument("--attach", nargs="*")
    report.set_defaults(func=cmd_report)

    reminder = sub.add_parser("reminder", parents=[parent], help="Send a reminder email")
    reminder.add_argument("--to", nargs="+", required=True)
    reminder.add_argument("--task", required=True)
    reminder.add_argument("--due", required=True)
    reminder.add_argument("--notes")
    reminder.set_defaults(func=cmd_reminder)

    bulk = sub.add_parser("bulk", parents=[parent], help="Send bulk emails from CSV/JSON")
    bulk.add_argument("--recipients", required=True, help="Path to CSV or JSON file")
    bulk.add_argument("--subject", required=True, help="Subject with {name} placeholders")
    bulk.add_argument("--body", required=True, help="Body with {name} placeholders")
    bulk.add_argument("--html-file", help="Optional HTML template file")
    bulk.add_argument("--attach", nargs="*")
    bulk.add_argument("--delay", type=float, default=1.0, help="Seconds between sends")
    bulk.set_defaults(func=cmd_bulk)

    sched = sub.add_parser("schedule", parents=[parent], help="Schedule daily reports or reminders")
    sched.add_argument("--type", choices=["report", "reminder"], required=True)
    sched.add_argument("--time", required=True, help="Time in HH:MM (24h)")
    sched.add_argument("--to", nargs="+", required=True)
    sched.add_argument("--title", help="Report title (for report type)")
    sched.add_argument("--summary", help="Report summary (for report type)")
    sched.add_argument("--task", help="Task title (for reminder type)")
    sched.add_argument("--due", help="Due date (for reminder type)")
    sched.add_argument("--notes")
    sched.add_argument("--attach", nargs="*")
    sched.set_defaults(func=cmd_schedule)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
