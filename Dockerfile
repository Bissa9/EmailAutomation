FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY email_bot/ email_bot/
COPY templates/ templates/
COPY data/ data/
COPY main.py .

RUN mkdir -p credentials attachments

ENTRYPOINT ["python", "main.py"]
