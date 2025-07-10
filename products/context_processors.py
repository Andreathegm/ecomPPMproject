from decimal import Decimal

from django.db.models import Max

from products.models import Category, Product


def categories_context(request):
    categories = Category.objects.all().order_by('name')
    return {
        'categories': categories
    }


def max_product_price(self):
    max_price = Product.objects.aggregate(Max('price'))['price__max']
    max_price_ = max_price if max_price is not None else Decimal('0.00')
    return {
        'max_price': max_price_
    }
