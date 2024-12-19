# Build stage
FROM python:3.10.0 AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

RUN pip install --upgrade pip

# Copy requirements file and install dependencies
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy only necessary project files
COPY backend/ /usr/src/app/backend/

# Установить рабочую директорию для Django
WORKDIR /usr/src/app/backend/

# Собрать статические файлы
RUN python manage.py collectstatic --no-input \
   && find . -type d -name __pycache__ -exec rm -r {} + \
   && rm -rf /root/.cache /tmp/*

# Expose the port the app runs on
EXPOSE 8000

# Скопировать entrypoint.sh и сделать его исполнимым
COPY backend/entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Установить entrypoint для контейнера
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# Healthcheck to monitor the health of the running application
HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://localhost:8000/admin || exit 1
