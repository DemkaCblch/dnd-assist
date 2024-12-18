# Build stage
FROM python:3.10.0 AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt .

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
COPY . .

# Collect static files and clean up in single layer
RUN python manage.py collectstatic --noinput \
    && find . -type d -name __pycache__ -exec rm -r {} + \
    && rm -rf /root/.cache /tmp/*

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://localhost:8000/admin || exit 1

WORKDIR /usr/src/app
