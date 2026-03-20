# Déploiement sur Render.com

## 1. Préparation du Projet

Le projet est maintenant configuré pour Render avec :
- `render.yaml` : Configuration automatique
- `build.sh` : Script de build
- `gunicorn` : Serveur WSGI pour la production

## 2. Variables d'Environnement Requises

Sur Render, configurez ces variables d'environnement :

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=systeme-code-barre.onrender.com,localhost,127.0.0.1
DATABASE_URL=postgres://user:pass@host:port/dbname
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=secure_password
```

## 3. Déploiement Automatique

### Option A : Avec render.yaml (Recommandé)

1. Connectez votre dépôt GitHub à Render
2. Le fichier `render.yaml` configurera automatiquement :
   - Le service web Python
   - La base de données PostgreSQL
   - Les variables d'environnement

### Option B : Configuration Manuelle

1. **Créer la Base de Données :**
   - Type : PostgreSQL
   - Plan : Free
   - Nom : `systeme-code-barre-db`

2. **Créer le Service Web :**
   - Type : Web Service
   - Runtime : Python 3
   - Build Command : `./build.sh`
   - Start Command : `gunicorn barcode_project.wsgi:application`

## 4. Configuration Post-Déploiement

### Accès Admin
- URL : `https://systeme-code-barre.onrender.com/admin/`
- Utilisateur : Défini par `DJANGO_SUPERUSER_USERNAME`
- Mot de passe : Défini par `DJANGO_SUPERUSER_PASSWORD`

### Fichiers Statiques
- Gérés automatiquement par WhiteNoise
- Collectés lors du build avec `collectstatic`

### Base de Données
- Migrations appliquées automatiquement lors du build
- Connexion via `DATABASE_URL`

## 5. Commandes Utiles

### Logs en Temps Réel
```bash
# Via Render Dashboard ou CLI
render logs -s your-service-name
```

### Redéploiement Manuel
```bash
# Via Render Dashboard : "Manual Deploy"
# Ou push sur la branche main
```

### Shell Django sur Render
```bash
# Via Render Shell
python manage.py shell
```

## 6. Dépannage

### Erreur ALLOWED_HOSTS
- Vérifiez que `ALLOWED_HOSTS` contient votre domaine Render
- Le domaine est maintenant codé en dur dans `settings.py`

### Erreur de Base de Données
- Vérifiez que `DATABASE_URL` est correctement configurée
- Assurez-vous que la base PostgreSQL est créée

### Erreur de Build
- Vérifiez les logs de build dans Render Dashboard
- Assurez-vous que `build.sh` est exécutable

### Fichiers Statiques Manquants
- WhiteNoise gère les fichiers statiques automatiquement
- `collectstatic` est exécuté lors du build

## 7. Monitoring

### Santé du Service
- Render surveille automatiquement la santé
- Redémarre en cas de crash

### Métriques
- CPU, RAM, et trafic disponibles dans le dashboard
- Logs d'accès et d'erreur

### Sauvegardes
- Base de données sauvegardée automatiquement (plan payant)
- Exportez manuellement si nécessaire :
  ```bash
  pg_dump $DATABASE_URL > backup.sql
  ```

## 8. Mise à Jour

1. Push les modifications sur GitHub
2. Render redéploie automatiquement
3. Les migrations sont appliquées automatiquement
4. Les fichiers statiques sont recollectés

## 9. Domaine Personnalisé

Pour utiliser votre propre domaine :
1. Ajoutez-le dans Render Dashboard
2. Mettez à jour `ALLOWED_HOSTS`
3. Configurez vos DNS