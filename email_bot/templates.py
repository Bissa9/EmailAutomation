from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from config.settings import TEMPLATES_DIR


def get_template_env() -> Environment:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    return Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def render_template(template_name: str, **context) -> str:
    env = get_template_env()
    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        raise FileNotFoundError(
            f"Template '{template_name}' not found in {TEMPLATES_DIR}"
        )
    return template.render(**context)


def render_report_email(
    recipient_name: str,
    report_title: str,
    report_summary: str,
    report_date: str,
) -> tuple[str, str]:
    subject = f"Report: {report_title} — {report_date}"
    body = render_template(
        "report.html",
        recipient_name=recipient_name,
        report_title=report_title,
        report_summary=report_summary,
        report_date=report_date,
    )
    return subject, body


def render_reminder_email(
    recipient_name: str,
    task_title: str,
    due_date: str,
    notes: str = "",
) -> tuple[str, str]:
    subject = f"Reminder: {task_title} due {due_date}"
    body = render_template(
        "reminder.html",
        recipient_name=recipient_name,
        task_title=task_title,
        due_date=due_date,
        notes=notes,
    )
    return subject, body
