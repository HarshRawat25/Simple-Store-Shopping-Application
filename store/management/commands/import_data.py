import csv
import os
import random
from django.core.management.base import BaseCommand
from store.models import Product
from django.core.files import File
from pathlib import Path

class Command(BaseCommand):
    help = 'Import products from Dataset/data.csv'

    def handle(self, *args, **options):
        csv_file_path = 'Dataset/data.csv'
        dataset_dir = Path('Dataset')

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found at {csv_file_path}'))
            return

        # Updated Price ranges in INR to be more realistic
        price_ranges = {
            'T-shirt': (200, 1500),
            'Jacket': (1999, 5999),
            'Default': (299, 4999),
        }

        # First, clear existing products to avoid duplicates and apply new prices
        Product.objects.all().delete()
        self.stdout.write('Clearing old products...')

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0

            for row in reader:
                p_type = row['Type']
                design = row['Design']

                # 1. Generate a Name
                name = f"{design} {p_type}"

                # 2. Generate a Price in INR based on updated ranges
                low, high = price_ranges.get(p_type, price_ranges['Default'])
                price = random.randint(low, high)

                # 3. Generate a Description
                description = f"High-quality {design} {p_type}. Comfortable and stylish, perfect for any occasion."

                # 4. Try to find a matching image
                image_folder = dataset_dir / p_type
                image_path = None

                if image_folder.exists():
                    images = list(image_folder.glob('*.jpg')) + list(image_folder.glob('*.png'))
                    if images:
                        image_path = random.choice(images)

                # Create the Product
                product = Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    stock=random.randint(10, 100)
                )

                if image_path:
                    with open(image_path, 'rb') as img_file:
                        product.image.save(image_path.name, File(img_file), save=True)

                count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} products with updated prices!'))
