#!/usr/bin/env python
"""Script pour créer les paramètres de l'entreprise"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barcode_project.settings')
django.setup()

from products.models import CompanySettings

# Créer ou récupérer les paramètres
company, created = CompanySettings.objects.get_or_create(
    id=1,
    defaults={
        'name': 'Mon Entreprise',
        'phone_number_1': '653280942',
        'phone_number_2': '658039370'
    }
)

if created:
    print("✓ Paramètres de l'entreprise créés avec succès!")
    print("  Allez dans Paramètres pour ajouter votre logo.")
else:
    print("✓ Paramètres de l'entreprise déjà existants.")
    print(f"  Nom: {company.name}")
    if company.logo:
        print(f"  Logo: {company.logo.url}")
    else:
        print("  Logo: Non configuré - Allez dans Paramètres pour l'ajouter")
