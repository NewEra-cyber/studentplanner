#!/bin/bash

echo "🚀 STARTING COMPREHENSIVE PRODUCTIVITY APP..."

# Start Redis
echo "📦 Starting Redis..."
redis-server --daemonize yes

# Start Celery Worker
echo "⚡ Starting Celery Worker..."
celery -A productivity_app worker --loglevel=info --concurrency=4 &

# Start Celery Beat
echo "⏰ Starting Celery Beat Scheduler..."
celery -A productivity_app beat --loglevel=info &

# Apply migrations
echo "🗃️ Applying database migrations..."
python manage.py migrate

# Load JKUAT data
echo "📊 Loading JKUAT timetable and roadmap..."
python manage.py load_jkuat_data

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start Django development server
echo "🌐 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000