from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from products.models import Product


def get_filtered_products(self, query_set=None):
    qs = query_set or Product.objects.all()# Include anche prodotti non disponibili

    discount_flag = self.request.GET.get('discount')
    if discount_flag in ['1', 'true', 'True', 'yes']:
        qs = filter_discount(qs)

    # ---- Filtro per ricerca ----
    search_query = self.request.GET.get('search')
    if search_query:
        qs = qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # ---- Filtro per categoria ----
    category_slug = self.request.GET.get('category')
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    # ---- Filtro per prezzo massimo ----
    max_price = self.request.GET.get('max_price')
    if max_price:
        try:
            max_price = float(max_price)
            qs = qs.filter(price__lte=max_price)
        except ValueError:
            pass

    # ---- Ordinamento ----
    order = self.request.GET.get('order')
    if order == '1':        # Prezzo crescente
        qs = qs.order_by('price')
    elif order == '2':      # Prezzo decrescente
        qs = qs.order_by('-price')
    elif order == '3':      # Più recenti
        qs = qs.order_by('-created_at')
    else:                   # Default
        qs = qs.order_by('name')

    return qs

def calculate_shipping_cost():
    """
    Placeholder function to calculate shipping cost.
    You can implement your own logic here.
    """
    return Decimal('5.00')  # Example fixed shipping cost

def filter_discount(qs):
    now = timezone.now()
    date_q  = Q(discount_start_date__lte=now, discount_end_date__gte=now)
    date_q |= Q(discount_start_date__lte=now, discount_end_date__isnull=True)
    date_q |= Q(discount_start_date__isnull=True, discount_end_date__gte=now)
    date_q |= Q(discount_start_date__isnull=True, discount_end_date__isnull=True)

    qs = qs.filter(
        Q(is_discount_active=True),
        Q(discount_percentage__gt=0),
        date_q
    )
    return qs
