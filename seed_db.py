from store.models import Product
from django.core.files.base import ContentFile

products_data = [
    ('Classic White T-Shirt', '100% Organic cotton, breathable and stylish.', 25.00, 50),
    ('Slim Fit Blue Jeans', 'Durable denim with a modern slim fit.', 45.00, 30),
    ('Summer Floral Dress', 'Lightweight and breezy for warm weather.', 35.00, 20),
    ('Running Sneakers', 'High-performance sneakers for daily jogging.', 80.00, 25),
    ('Leather Formal Shoes', 'Premium leather shoes for a professional look.', 120.00, 15),
    ('Comfort Flip-Flops', 'Perfect for the beach and indoor use.', 15.00, 100),
    ('Organic Aloe Vera Soap', 'Soothing and hydrating for sensitive skin.', 5.00, 200),
    ('Lavender Relaxing Soap', 'Calming scent to help you unwind.', 6.00, 150),
    ('Charcoal Detox Soap', 'Deep cleanses and removes impurities.', 7.00, 120),
]

for name, desc, price, stock in products_data:
    product = Product.objects.create(name=name, description=desc, price=price, stock=stock)
    filename = f'products/{name.replace(" ", "_").lower()}.jpg'
    product.image.save(filename, ContentFile(b'fake-image-content'), save=False)
    product.save()

print('Products added successfully!')
