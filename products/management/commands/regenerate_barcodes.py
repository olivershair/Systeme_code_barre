from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Régénère tous les codes-barres des produits avec la nouvelle taille'

    def handle(self, *args, **options):
        products = Product.objects.all()
        count = 0
        
        for product in products:
            product.barcode_image.delete(save=False)
            product.generate_barcode()
            product.save()
            count += 1
            self.stdout.write(f'Code-barres régénéré pour: {product.reference}')
        
        self.stdout.write(self.style.SUCCESS(f'\n{count} codes-barres régénérés avec succès!'))
