# Système de Gestion d'Étiquettes avec Codes-barres

Application Django professionnelle pour la génération et la gestion d'étiquettes de produits avec codes-barres.

## Fonctionnalités

- ✅ Création et gestion de produits (référence, nom, taille, prix)
- ✅ Génération automatique de codes-barres (Code 128)
- ✅ Prévisualisation des étiquettes avec logo entreprise
- ✅ Export PDF et Image des étiquettes
- ✅ Impression multiple (21 étiquettes par page A4)
- ✅ Import/Export Excel
- ✅ Scanner de codes-barres via caméra
- ✅ Interface Bootstrap 5 responsive
- ✅ Système d'authentification

## Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer la base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 5. Créer les dossiers média

```bash
mkdir media
mkdir media/logos
mkdir media/barcodes
mkdir static
```

### 6. Lancer le serveur

```bash
python manage.py runserver
```

Accédez à l'application: http://127.0.0.1:8000

## Configuration Entreprise

1. Connectez-vous avec votre compte
2. Allez dans "Paramètres" dans le menu
3. Ajoutez le logo de votre entreprise
4. Configurez les numéros de téléphone (653280942 / 658039370)

## Utilisation

### Créer un produit

1. Cliquez sur "Nouveau Produit"
2. Remplissez les informations (référence, nom, taille, prix)
3. Cliquez sur "Enregistrer et Générer le Code-barres"
4. Le code-barres est généré automatiquement

### Importer depuis Excel

1. Préparez un fichier Excel avec les colonnes:
   - reference
   - nom
   - taille
   - prix

2. Cliquez sur "Importer" dans le menu
3. Sélectionnez votre fichier Excel
4. Les codes-barres sont générés automatiquement

### Imprimer des étiquettes

#### Étiquette unique
- Allez sur la prévisualisation du produit
- Cliquez sur "Télécharger PDF" ou "Télécharger Image"

#### Impression multiple (21 étiquettes/page)
- Cliquez sur "Imprimer Multiple"
- Sélectionnez les produits
- Générez le PDF avec 21 étiquettes par page A4

### Scanner un code-barres

1. Cliquez sur "Scanner" dans le menu
2. Autorisez l'accès à la caméra
3. Positionnez le code-barres devant la caméra
4. Le produit s'affiche automatiquement

## Structure du Projet

```
barcode_system/
├── manage.py
├── requirements.txt
├── README.md
├── barcode_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── products/
    ├── models.py          # Modèles Product et CompanySettings
    ├── views.py           # Vues de l'application
    ├── urls.py            # Routes URL
    ├── forms.py           # Formulaires
    ├── utils.py           # Fonctions utilitaires (PDF, Excel)
    ├── admin.py           # Configuration admin Django
    └── templates/
        └── products/
            ├── base.html
            ├── product_list.html
            ├── product_form.html
            ├── preview_label.html
            ├── scan_barcode.html
            ├── import_excel.html
            └── ...
```

## Technologies Utilisées

- Django 4.2+
- Bootstrap 5
- python-barcode (génération codes-barres)
- ReportLab (génération PDF)
- openpyxl & pandas (import/export Excel)
- Pillow (traitement images)
- jsQR (scan codes-barres)

## Sécurité

- Authentification requise pour toutes les pages
- Protection CSRF activée
- Validation des fichiers importés
- Sessions sécurisées

## Support

Pour toute question ou problème, consultez la documentation Django ou contactez l'administrateur système.

## Licence

Projet développé pour la gestion interne d'étiquettes produits.
