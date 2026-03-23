#!/usr/bin/env bash
set -o errexit

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🔧 Application des migrations..."
python manage.py migrate

echo "🏢 Initialisation des paramètres entreprise..."
python create_company_settings.py

echo "👤 Création du superuser..."
python manage.py createsuperuser --noinput || true

echo "✅ Build terminé!"
