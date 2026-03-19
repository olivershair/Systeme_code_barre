from django.db import models
from django.contrib.auth.models import User
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File


class CompanySettings(models.Model):
    """Configuration de l'entreprise"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    logo = models.ImageField(upload_to='logos/', verbose_name="Logo")
    phone_number_1 = models.CharField(max_length=20, default="653280942")
    phone_number_2 = models.CharField(max_length=20, default="658039370")
    
    class Meta:
        verbose_name = "Paramètres de l'entreprise"
        verbose_name_plural = "Paramètres de l'entreprise"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Modèle pour les produits"""
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    size = models.CharField(max_length=50, verbose_name="Taille")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reference} - {self.name}"

    def generate_barcode(self):
        """Génère le code-barres pour le produit avec dimensions optimisées"""
        CODE128 = barcode.get_barcode_class('code128')
        barcode_value = f"{self.reference}"
        
        # Options pour optimiser le code-barres: hauteur -20%, longueur +30%, sans texte
        writer_options = {
            'module_width': 0.13,   # Largeur des barres augmentée (+30%)
            'module_height': 4.0,   # Hauteur des barres réduite (-20%)
            'quiet_zone': 1.5,      # Marge autour
            'font_size': 0,         # Pas de texte sous le code-barres
            'text_distance': 0,     # Pas d'espace pour le texte
            'write_text': False,    # Désactiver l'affichage du texte
        }
        
        rv = BytesIO()
        CODE128(barcode_value, writer=ImageWriter()).write(rv, options=writer_options)
        
        self.barcode_image.save(f'{self.reference}.png', File(rv), save=False)
        return self.barcode_image
    
    def save(self, *args, **kwargs):
        if not self.barcode_image:
            self.generate_barcode()
        super().save(*args, **kwargs)
