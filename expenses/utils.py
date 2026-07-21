from expenses.models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Food', 'icon': 'bi-cup-hot-fill', 'color': '#ff7675'},
    {'name': 'Shopping', 'icon': 'bi-bag-fill', 'color': '#74b9ff'},
    {'name': 'Transport', 'icon': 'bi-car-front-fill', 'color': '#00b894'},
    {'name': 'Rent', 'icon': 'bi-house-door-fill', 'color': '#a29bfe'},
    {'name': 'Education', 'icon': 'bi-book-fill', 'color': '#fdcb6e'},
    {'name': 'Medical', 'icon': 'bi-heart-pulse-fill', 'color': '#ff7675'},
    {'name': 'Entertainment', 'icon': 'bi-controller', 'color': '#e17055'},
    {'name': 'Travel', 'icon': 'bi-airplane-fill', 'color': '#00cec9'},
    {'name': 'Bills', 'icon': 'bi-receipt-cutoff', 'color': '#d63031'},
    {'name': 'Others', 'icon': 'bi-grid-fill', 'color': '#6c5ce7'},
]

def ensure_default_categories(user=None):
    """Ensures default categories exist in the database."""
    created_categories = []
    for cat_data in DEFAULT_CATEGORIES:
        cat, created = Category.objects.get_or_create(
            category_name=cat_data['name'],
            user=user,
            defaults={
                'icon': cat_data['icon'],
                'color': cat_data['color']
            }
        )
        created_categories.append(cat)
    return created_categories
