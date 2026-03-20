# Configuration PostgreSQL pour la Production

## 1. Installation des Dépendances

```bash
pip install -r requirements.txt
```

## 2. Configuration de la Base de Données

### Variables d'Environnement Requises

Copiez `.env.production` vers `.env` et configurez :

```env
DATABASE_URL=postgres://username:password@hostname:5432/database_name
```

### Format de l'URL PostgreSQL

```
postgres://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
```

**Exemples :**
- Local : `postgres://myuser:mypassword@localhost:5432/mydatabase`
- Render : `postgres://user:pass@dpg-xxxxx-a.oregon-postgres.render.com/dbname`
- Heroku : `postgres://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/dbname`

## 3. Création de la Base de Données

### Sur Render.com (Recommandé)

1. Connectez-vous à [Render.com](https://render.com)
2. Créez un nouveau service PostgreSQL
3. Copiez l'URL de connexion fournie
4. Ajoutez-la à votre variable `DATABASE_URL`

### Localement avec Docker

```bash
docker run --name postgres-barcode \
  -e POSTGRES_DB=barcode_system \
  -e POSTGRES_USER=barcode_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  -d postgres:15
```

## 4. Migration des Données

### Depuis SQLite vers PostgreSQL

```bash
# 1. Sauvegarde des données SQLite
python manage.py dumpdata --natural-foreign --natural-primary > data.json

# 2. Configuration PostgreSQL
export DATABASE_URL="postgres://user:pass@host:port/dbname"

# 3. Migrations
python manage.py migrate

# 4. Chargement des données
python manage.py loaddata data.json
```

### Script de Déploiement Automatique

```bash
python deploy.py
```

## 5. Variables d'Environnement de Production

```env
# Base de données
DATABASE_URL=postgres://user:pass@host:port/dbname

# Sécurité
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# SSL/HTTPS
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SECURE_HSTS_SECONDS=31536000

# Superutilisateur (optionnel)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=secure_admin_password
```

## 6. Commandes Utiles

```bash
# Test de connexion
python manage.py dbshell

# Vérification des migrations
python manage.py showmigrations

# Création d'un superutilisateur
python manage.py createsuperuser

# Collecte des fichiers statiques
python manage.py collectstatic

# Sauvegarde de la base
pg_dump $DATABASE_URL > backup.sql

# Restauration
psql $DATABASE_URL < backup.sql
```

## 7. Monitoring et Maintenance

### Logs de Base de Données

```python
# Dans settings.py pour debug
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Performance

- Utilisez `CONN_MAX_AGE` pour la persistance des connexions
- Configurez un pool de connexions si nécessaire
- Surveillez les requêtes lentes avec `django-debug-toolbar`

## 8. Sécurité

- Utilisez toujours SSL en production (`sslmode=require`)
- Limitez les connexions par IP
- Utilisez des mots de passe forts
- Sauvegardez régulièrement
- Surveillez les logs d'accès