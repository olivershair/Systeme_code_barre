from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Setup production environment: run migrations and create superuser'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting production setup...'))
        
        # Vérifier la connexion à la base de données
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✅ Database connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection failed: {e}'))
            return
        
        # Appliquer les migrations
        self.stdout.write('🗄️ Applying migrations...')
        from django.core.management import call_command
        try:
            call_command('migrate', verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS('✅ Migrations applied successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))
            return
        
        # Créer le superutilisateur
        self.stdout.write('👤 Creating superuser...')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Superuser "{username}" created successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Superuser "{username}" already exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Superuser creation failed: {e}'))
        
        # Créer un utilisateur de test si en mode debug
        if os.environ.get('DEBUG', 'False').lower() == 'true':
            test_username = 'test'
            try:
                if not User.objects.filter(username=test_username).exists():
                    User.objects.create_user(
                        username=test_username,
                        password='test123'
                    )
                    self.stdout.write(self.style.SUCCESS(f'✅ Test user "{test_username}" created'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️ Test user "{test_username}" already exists'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Test user creation failed: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Production setup completed!'))