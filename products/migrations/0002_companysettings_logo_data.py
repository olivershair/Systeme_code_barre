from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companysettings',
            name='logo_data',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='companysettings',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos/', verbose_name='Logo'),
        ),
    ]
