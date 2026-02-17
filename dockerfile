# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
RUN pip install gunicorn whitenoise

# Copy project
COPY . /app/

# Run collectstatic
# We set a dummy SECRET_KEY if not present to allow collectstatic to run during build
RUN DJANGO_SETTINGS_MODULE=school_sms.settings python manage.py collectstatic --noinput

# Start application with automatic migrations and superuser creation
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py ensure_superuser && python manage.py seed_brillspay && daphne -b 0.0.0.0 -p $PORT school_sms.asgi:application"]
