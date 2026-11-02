FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OTEL_SERVICE_NAME=lab3-task1-dice

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && opentelemetry-bootstrap -a install

COPY app.py ./

EXPOSE 8080

CMD ["opentelemetry-instrument", \
     "flask", "--app", "app", "run", \
     "--host", "0.0.0.0", "--port", "8080"]
