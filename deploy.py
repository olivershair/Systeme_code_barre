#!/usr/bin/env python
"""
Script de déploiement pour la production
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def deploy():
    """Exécute les commandes de déploiement"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barcode_project.settings')
    django.setup()
    
    print("🚀 Début du déploiement...")
    
    # Collecte des fichiers statiques
    print("📁 Collecte des fichiers statiques...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Migrations de la base de données
    print("🗄️ Application des migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Création du superutilisateur si nécessaire
    print("👤 Vérification du superutilisateur...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("Création du superutilisateur...")
            User.objects.create_superuser(
                username=os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
                email=os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
                password=os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            )
            print("✅ Superutilisateur créé")
        else:
            print("✅ Superutilisateur existe déjà")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création du superutilisateur: {e}")
    
    print("✅ Déploiement terminé avec succès!")

if __name__ == '__main__':
    deploy()