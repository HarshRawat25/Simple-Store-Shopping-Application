from django.core.management.base import BaseCommand, CommandError

from store.models import Product


class Command(BaseCommand):
    help = 'Assign local fallback images to the six electronics products shown on the homepage.'

    image_assignments = {
        'Lenovo Legion 5 15IRX9': 'products/electronics/home-lenovo-legion.png',
        'SONY Playstation 5 Digital Edition': 'products/electronics/home-playstation-console.png',
        'MSI Vector 16 HX AI': 'products/electronics/home-msi-vector.png',
        'SONY DualSense Wireless Gaming Controller': 'products/electronics/home-red-controller.png',
        'SONY Portal Wireless Gaming Controller': 'products/electronics/home-gaming-handheld.png',
        'Lenovo LOQ 15IRX9': 'products/electronics/home-lenovo-loq.png',
    }

    def handle(self, *args, **options):
        updated = 0
        for product_prefix, image_path in self.image_assignments.items():
            product = Product.objects.filter(name__startswith=product_prefix).order_by('-id').first()
            if not product:
                raise CommandError(f'Product not found: {product_prefix}')

            product.image = image_path
            product.save(update_fields=['image'])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Assigned {updated} local homepage electronics images.'))
