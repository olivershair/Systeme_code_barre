#!/usr/bin/env python
"""
Script de vérification de la configuration pour Render
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barcode_project.settings')
django.setup()

def check_configuration():
    print("🔍 Vérification de la configuration...")
    print(f"DEBUG = {settings.DEBUG}")
    print(f"ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
    
    # Vérification de la base de données
    db_config = settings.DATABASES['default']
    print(f"Database ENGINE = {db_config['ENGINE']}")
    
    if 'postgresql' in db_config['ENGINE']:
        print("✅ PostgreSQL configuré")
        print(f"Database NAME = {db_config.get('NAME', 'N/A')}")
        print(f"Database HOST = {db_config.get('HOST', 'N/A')}")
    else:
        print("⚠️ SQLite configuré (pas optimal pour production)")
    
    # Vérification des variables d'environnement
    env_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'DJANGO_SUPERUSER_USERNAME',
        'DJANGO_SUPERUSER_PASSWORD'
    ]
    
    print("\n🔑 Variables d'environnement:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Masquer les valeurs sensibles
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"{var} = {'*' * min(len(value), 10)}")
            elif 'DATABASE_URL' in var:
                print(f"{var} = {value[:30]}...")
            else:
                print(f"{var} = {value}")
        else:
            print(f"{var} = ❌ NON DÉFINIE")
    
    # Test de connexion à la base de données
    print("\n🗄️ Test de connexion à la base de données...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Connexion à la base de données réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
    
    print("\n✅ Vérification terminée")

if __name__ == '__main__':
    check_configuration()