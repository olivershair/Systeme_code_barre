#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check configuration
echo "🔍 Checking configuration..."
python check_config.py

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Setup production (migrations + superuser)
echo "🔧 Setting up production environment..."
python manage.py setup_production

echo "✅ Build completed successfully!"