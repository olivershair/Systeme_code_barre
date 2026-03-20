# Configuration des Variables d'Environnement

## Installation

1. Copiez le fichier `.env.example` vers `.env` :
   ```bash
   cp .env.example .env
   ```

2. Modifiez les valeurs dans `.env` selon votre environnement.

## Variables Disponibles

### Django Configuration
- `SECRET_KEY` : Clé secrète Django (générez-en une nouvelle pour la production)
- `DEBUG` : Mode debug (True/False)

### Base de Données
- `DATABASE_URL` : URL de connexion à la base de données
  - SQLite : `sqlite:///db.sqlite3`
  - PostgreSQL : `postgres://user:password@host:port/dbname`

### Hosts Autorisés
- `ALLOWED_HOSTS` : Liste des domaines autorisés (séparés par des virgules)

### Fichiers Statiques
- `STATIC_URL` : URL des fichiers statiques
- `MEDIA_URL` : URL des fichiers média

### Localisation
- `LANGUAGE_CODE` : Code de langue (ex: fr-fr, en-us)
- `TIME_ZONE` : Fuseau horaire (ex: UTC, Europe/Paris)

### Authentification
- `LOGIN_URL` : URL de connexion
- `LOGIN_REDIRECT_URL` : URL de redirection après connexion

## Génération d'une Clé Secrète

Pour générer une nouvelle clé secrète Django :

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Déploiement

Pour le déploiement en production :
1. Définissez `DEBUG=False`
2. Générez une nouvelle `SECRET_KEY`
3. Configurez `ALLOWED_HOSTS` avec votre domaine
4. Configurez `DATABASE_URL` si vous utilisez PostgreSQL