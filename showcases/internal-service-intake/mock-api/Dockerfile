FROM python:3.12.6-slim
WORKDIR /app
COPY app.py /app/app.py
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "/app/app.py", "--db-path", "/data/intake.db", "--api-key", "${MOCK_API_KEY:-local-demo-api-key}"]
