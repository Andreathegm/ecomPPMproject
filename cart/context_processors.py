from cart.utils import get_existing_cart


def cart_context(request):
    cart = get_existing_cart(request)

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
