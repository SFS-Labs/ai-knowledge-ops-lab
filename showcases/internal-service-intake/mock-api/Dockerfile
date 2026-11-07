FROM python:3.12.6-slim
WORKDIR /app
COPY app.py /app/app.py
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8080
# Compose supplies the required --api-key; standalone images fail closed.
CMD ["python", "/app/app.py"]
