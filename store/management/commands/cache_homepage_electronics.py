from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from store.models import Product


class Command(BaseCommand):
    help = 'Download local copies of the six electronics images shown on the homepage.'

    def handle(self, *args, **options):
        products = (
            Product.objects.exclude(category__isnull=True)
            .exclude(category__name__iexact='Clothing')
            .order_by('-id')[:6]
        )
        downloaded = 0

        for product in products:
            image_url = product.image_url
            if not image_url.startswith(('https://', 'http://')):
                self.stdout.write(f'Skipped {product.name}: local image already exists.')
                continue

            image_urls = [image_url]
            if '/prod/http' in image_url:
                # The exported Croma proxy URL is no longer available, but it
                # contains the original media.croma.com URL after /prod/.
                image_urls.append(image_url.split('/prod/', 1)[1])

            image_data = None
            content_type = None
            for candidate_url in image_urls:
                try:
                    request = Request(candidate_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urlopen(request, timeout=20) as response:
                        image_data = response.read()
                        content_type = response.headers.get_content_type()
                    break
                except (HTTPError, URLError, TimeoutError) as error:
                    last_error = error

            if image_data is None:
                self.stderr.write(self.style.WARNING(f'Could not download {product.name}: {last_error}'))
                continue

            extension = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp',
            }.get(content_type, '.jpg')
            filename = f'electronics/home-{product.pk}{extension}'
            product.image.save(filename, ContentFile(image_data), save=True)
            downloaded += 1
            self.stdout.write(f'Cached image for {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Cached {downloaded} homepage electronics images.'))
