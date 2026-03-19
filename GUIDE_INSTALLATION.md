# Guide d'Installation Détaillé

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Navigateur web moderne (Chrome, Firefox, Edge)

## Installation Étape par Étape

### 1. Télécharger le Projet

Téléchargez et extrayez le projet dans un dossier de votre choix.

### 2. Ouvrir un Terminal

- Windows: Ouvrez PowerShell ou CMD dans le dossier du projet
- Linux/Mac: Ouvrez le Terminal dans le dossier du projet

### 3. Créer un Environnement Virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Vous devriez voir `(venv)` apparaître dans votre terminal.

### 4. Installer les Dépendances

```bash
pip install -r requirements.txt
```

Attendez que toutes les bibliothèques soient installées.

### 5. Initialiser la Base de Données

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un Compte Administrateur

```bash
python manage.py createsuperuser
```

Suivez les instructions:
- Nom d'utilisateur: admin (ou votre choix)
- Email: votre@email.com
- Mot de passe: (choisissez un mot de passe sécurisé)

### 7. Créer les Dossiers Nécessaires

```bash
# Windows
mkdir media
mkdir media\logos
mkdir media\barcodes
mkdir static

# Linux/Mac
mkdir -p media/logos media/barcodes static
```

### 8. Lancer le Serveur

```bash
python manage.py runserver
```

### 9. Accéder à l'Application

Ouvrez votre navigateur et allez à: http://127.0.0.1:8000

## Configuration Initiale

### 1. Connexion

- Utilisez le nom d'utilisateur et mot de passe créés à l'étape 6

### 2. Configurer l'Entreprise

1. Cliquez sur "Paramètres" dans le menu
2. Remplissez:
   - Nom de l'entreprise
   - Téléchargez le logo (PNG ou JPG)
   - Numéros de téléphone (par défaut: 653280942 / 658039370)
3. Cliquez sur "Enregistrer"

### 3. Créer Votre Premier Produit

1. Cliquez sur "Nouveau Produit"
2. Remplissez les informations:
   - Référence: REF001
   - Nom: T-Shirt Classique
   - Taille: M
   - Prix: 5000
3. Cliquez sur "Enregistrer et Générer le Code-barres"
4. Le code-barres est généré automatiquement!

## Test de l'Import Excel

1. Utilisez le fichier `exemple_import.xlsx` fourni
2. Cliquez sur "Importer" dans le menu
3. Sélectionnez le fichier
4. Cliquez sur "Importer"
5. 5 produits avec codes-barres sont créés automatiquement!

## Résolution de Problèmes

### Erreur: "python n'est pas reconnu"

Installez Python depuis https://www.python.org/downloads/

### Erreur: "pip n'est pas reconnu"

```bash
python -m ensurepip --upgrade
```

### Erreur: "Port 8000 déjà utilisé"

```bash
python manage.py runserver 8080
```

Puis accédez à http://127.0.0.1:8080

### La caméra ne fonctionne pas

- Vérifiez que vous avez autorisé l'accès à la caméra
- Utilisez HTTPS en production
- Testez avec un autre navigateur

## Déploiement en Production

Pour déployer en production:

1. Modifiez `settings.py`:
   - `DEBUG = False`
   - Ajoutez votre domaine dans `ALLOWED_HOSTS`
   - Changez `SECRET_KEY`

2. Utilisez une vraie base de données (PostgreSQL, MySQL)

3. Configurez un serveur web (Nginx + Gunicorn)

4. Activez HTTPS pour le scanner de codes-barres

## Support

Pour toute question, consultez:
- Documentation Django: https://docs.djangoproject.com/
- README.md du projet
