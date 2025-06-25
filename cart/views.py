from django.shortcuts import render
from django.http import JsonResponse


from cart.models import Cart, CartItem
from products.models import Product
import json


# Create your views here.
def cart_detail(request):
    cart = _get_or_create_cart(request)

    # Placeholder for cart detail logic
    context = {
        'cart': cart,
        'cart_items': CartItem.objects.filter(cart=cart),

    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    cart = _get_or_create_cart(request)
    product = Product.objects.get(id=product_id)  # Assuming Product model exists
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, unit_price=product.price)

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    # cart_item.unit_price = product.price
    cart_item.save()

    context = {
        'cart': cart,
        'cart_items': CartItem.objects.filter(cart=cart),
    }

    return render(request, 'cart/cart.html', context)


def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = CartItem.objects.get(id=item_id)
        data = json.loads(request.body)
        new_quantity = data.get('quantity', cart_item.quantity)
        cart_item.quantity = new_quantity
        cart_item.save()
        return JsonResponse({
            'subtotal': cart_item.subtotal,
            'total': cart_item.cart.total,
            'tax': cart_item.cart.tax,
            'grand_total': cart_item.cart.grand_total,


        })


def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()

    cart = _get_or_create_cart(request)

    return JsonResponse({
        'total': cart.total,
        'tax': cart.tax,
        'grand_total': cart.grand_total,
    })


def _get_or_create_cart(request):
    session_key = request.session.session_key
    if not session_key:
        session_key = request.session.create()
    cart, created = Cart.objects.get_or_create(cart_id=session_key)
    return cart

# def cart_detail(request):
#     cart = _get_or_create_cart(request)
#     cart_items = CartItem.objects.filter(cart=cart)
#     total_price = sum(item.quantity * item.product.price for item in cart_items)
#
#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#     }
#     return render(request, 'cart/cart.html', context)
