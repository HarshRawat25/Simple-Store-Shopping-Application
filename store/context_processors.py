from .models import Category


def navigation_categories(request):
    """Make the category navigation available to every rendered template."""
    return {
        'categories': Category.objects.order_by('name'),
    }
