#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barcode_project.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully!')
else:
    print(f'Superuser {username} already exists.')

# Créer un utilisateur de test si pas en production
if os.environ.get('DEBUG', 'False').lower() == 'true':
    test_user = 'test'
    if not User.objects.filter(username=test_user).exists():
        User.objects.create_user(username=test_user, password='test123')
        print(f'Test user {test_user} created successfully!')
"

echo "✅ Build completed successfully!"