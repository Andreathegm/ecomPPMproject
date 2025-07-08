from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from cart.models import Cart, CartItem
from cart.utils import get_or_create_cart
from products.models import Product
import json


# Create your views here.
def cart_detail(request):
    cart = get_or_create_cart(request)

    # Placeholder for cart detail logic
    context = {
        'cart': cart,
        'cart_items': CartItem.objects.filter(cart=cart),

    }
    return render(request, 'cart/cart.html', context)


@require_POST
@csrf_protect
def add_to_cart(request, product_id):
    quantity = int(request.POST.get('quantity', 1))
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, unit_price=product.price)

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    # cart_item.unit_price = product.price
    cart_item.save()

    context = {
        'cart': cart,
        'cart_items': CartItem.objects.filter(cart=cart),
    }

    return render(request, 'cart/cart.html', context)


@require_POST
@csrf_protect
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    data = json.loads(request.body)
    new_quantity = data.get('quantity', cart_item.quantity)
    cart_item.quantity = new_quantity
    cart_item.save()
    return JsonResponse({
        'subtotal': cart_item.subtotal,
        'total': cart_item.cart.total,
        'tax': cart_item.cart.tax,
        'grand_total': cart_item.cart.grand_total,
        ##discount managment
        'discounted_total': cart_item.cart.discounted_total,
        'discounted_tax': cart_item.cart.discounted_tax,
        'discounted_grand_total': cart_item.cart.discounted_grand_total,

    })


@require_POST
@csrf_protect
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()

    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        return JsonResponse({
            'empty': True,
        })

    return JsonResponse({
        'cart_items_count': cart.items.count(),
        'total': cart.total,
        'tax': cart.tax,
        'grand_total': cart.grand_total,
    })

# def _get_or_create_cart(request):
#     if not request.session.session_key:
#         request.session.create()  # Ensure the session key is created
#     session_key = request.session.session_key
#     cart, created = Cart.objects.get_or_create(cart_id=session_key)
#     return cart

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
