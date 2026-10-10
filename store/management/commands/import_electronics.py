import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from store.models import Category, Product


class Command(BaseCommand):
    help = 'Import Croma electronics products and their matching dataset images.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='croma_products.csv',
            help='Path to the Croma CSV file (default: croma_products.csv).',
        )

    @staticmethod
    def parse_price(value):
        numeric_value = re.sub(r'[^0-9.]', '', value or '')
        try:
            return Decimal(numeric_value) if numeric_value else Decimal('0')
        except InvalidOperation:
            return Decimal('0')

    def handle(self, *args, **options):
        csv_path = Path(options['file'])
        if not csv_path.exists():
            raise CommandError(f'Dataset file not found: {csv_path}')

        electronics, _ = Category.objects.get_or_create(
            name='Electronics', defaults={'slug': 'electronics'}
        )
        existing_products = {
            product.name: product
            for product in Product.objects.filter(category=electronics)
        }
        products_to_create = []
        products_to_update = []

        with csv_path.open(encoding='utf-8-sig', newline='') as csv_file:
            for row in csv.DictReader(csv_file):
                name = (row.get('Title') or '').strip()[:255]
                image_url = (row.get('Image') or '').strip()
                if not name or not image_url:
                    continue

                product_values = {
                    'description': f"{row.get('Category', 'Electronics').replace('-', ' ').title()} product from the electronics catalogue.",
                    'price': self.parse_price(row.get('Price')),
                    'image': image_url,
                    'stock': 20,
                }
                existing_product = existing_products.get(name)
                if existing_product:
                    for field, value in product_values.items():
                        setattr(existing_product, field, value)
                    products_to_update.append(existing_product)
                else:
                    products_to_create.append(
                        Product(name=name, category=electronics, **product_values)
                    )

        if products_to_create:
            Product.objects.bulk_create(products_to_create, batch_size=500)
        if products_to_update:
            Product.objects.bulk_update(
                products_to_update,
                ['description', 'price', 'image', 'stock'],
                batch_size=500,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Electronics import complete: {len(products_to_create)} added, '
                f'{len(products_to_update)} updated.'
            )
        )
