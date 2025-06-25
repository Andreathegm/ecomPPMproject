from products.views import get_cart  # Usa la tua funzione esistente


def cart_context(request):
    cart = get_cart(request)

    if cart:
        cart_item_ids = set(cart.items.values_list('product_id', flat=True))
        item_count = cart.items.count()
    else:
        cart_item_ids = None
        item_count = 0

    return {
        'cart_item_ids': cart_item_ids,
        'cart_item_count': item_count,
    }
