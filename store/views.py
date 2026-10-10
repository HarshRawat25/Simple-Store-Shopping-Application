from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from .models import Product, Category, Order, OrderItem, Review
from django.http import JsonResponse
from django.db.models import Avg
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

CATEGORY_PAGE_SIZE = 24
DATASET_PENDING_CATEGORIES = {'Beauty & Health', 'Books', 'Home & Kitchen'}

@login_required
def home(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.all()
    if query:
        # Search deliberately returns every matching product instead of the
        # smaller curated collection used on the landing page.
        products = Product.objects.filter(name__icontains=query).order_by('name')
    else:
        # Keep the landing page to 12 products: six clothing and six
        # electronics. The imported Dataset/data.csv clothing products have
        # their own local image files; the older Clothing seed records use a
        # missing placeholder file, so they are excluded from this selection.
        clothing_products = list(
            Product.objects.filter(category__isnull=True).order_by('-id')[:6]
        )
        electronics_products = list(
            Product.objects.exclude(category__isnull=True)
            .exclude(category__name__iexact='Clothing')
            .order_by('-id')[:6]
        )
        products = clothing_products + electronics_products

    # Featured products for the carousel
    featured_products = Product.objects.filter(is_featured=True)[:5]

    return render(request, 'index.html', {
        'products': products,
        'categories': categories,
        'featured_products': featured_products,
        'query': query
    })

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Related products: same category, excluding current product
    related_products = []
    if product.category:
        related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]

    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products
    })

@login_required
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if category.name in DATASET_PENDING_CATEGORIES:
        # Do not mix in unrelated electronics while these datasets are pending.
        products = Product.objects.none()
    elif category.name == 'Clothing':
        # Imported clothing has local image files and is not assigned to the
        # old three-product Clothing seed category.
        products = list(
            Product.objects.filter(category__isnull=True).order_by('-id')[:CATEGORY_PAGE_SIZE]
        )
    else:
        products = list(
            Product.objects.filter(category=category).order_by('-id')[:CATEGORY_PAGE_SIZE]
        )

        # Several legacy categories only have two or three seed products.
        # Fill those pages to a useful 24-card collection with electronics
        # catalogue items, without duplicating their direct matches.
        if len(products) < CATEGORY_PAGE_SIZE:
            products.extend(
                Product.objects.filter(category__name__iexact='Electronics')
                .exclude(pk__in=[product.pk for product in products])
                .order_by('-id')[:CATEGORY_PAGE_SIZE - len(products)]
            )

    return render(request, 'index.html', {
        'products': products,
        'category': category,
        'categories': Category.objects.all(),
        'query': '',
    })

@login_required
def user_profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {
        'orders': orders
    })

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart

    if request.headers.get('content-type') == 'application/json':
        product = get_object_or_404(Product, pk=product_id)
        return JsonResponse({
            'status': 'success',
            'product_name': product.name,
            'cart_count': sum(cart.values())
        })

    return redirect('cart_view')

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart

    if request.headers.get('content-type') == 'application/json':
        return JsonResponse({
            'status': 'success',
            'cart_count': sum(cart.values())
        })

    return redirect('cart_view')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            price = product.current_price
            item_total = price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
        except Product.DoesNotExist:
            pass

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('home')

        total = 0
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_price=0 # Will update after items
        )

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            price = product.current_price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total += price * quantity

        order.total_price = total
        order.save()

        request.session['cart'] = {}
        return render(request, 'checkout.html', {'order': order})

    return render(request, 'checkout.html')

def login_view(request):
    """Authenticate a user and optionally persist the session for two weeks."""
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.POST.get('next') or request.GET.get('next')
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = resolve_url('home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        # A session-only cookie is used unless the user explicitly opts in.
        request.session.set_expiry(60 * 60 * 24 * 14 if request.POST.get('remember_me') else 0)
        return redirect(next_url)

    return render(request, 'login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    """Log out safely and return the visitor to the sign-in screen."""
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def add_review(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        product = get_object_or_404(Product, pk=product_id)
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
    return redirect('product_detail', pk=product_id)
