FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
# Create non-root user
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# Install system deps for cryptography if needed (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app

RUN chown -R app:app /app

USER app

ENTRYPOINT [ "python", "main.py" ]