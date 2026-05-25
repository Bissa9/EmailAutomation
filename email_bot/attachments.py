import mimetypes
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from pathlib import Path


def attach_files(message, file_paths: list[Path]) -> None:
    for path in file_paths:
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {path}")
        message.attach(_build_mime_part(path))


def _build_mime_part(path: Path):
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    main_type, sub_type = mime_type.split("/", 1)
    data = path.read_bytes()

    if main_type == "text":
        part = MIMEText(data.decode("utf-8", errors="replace"), _subtype=sub_type)
    elif main_type == "image":
        part = MIMEImage(data, _subtype=sub_type)
    elif main_type == "audio":
        part = MIMEAudio(data, _subtype=sub_type)
    elif main_type == "application":
        part = MIMEApplication(data, _subtype=sub_type)
    else:
        part = MIMEBase(main_type, sub_type)
        part.set_payload(data)

    part.add_header("Content-Disposition", "attachment", filename=path.name)
    return part
