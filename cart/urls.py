from django.urls import path
from . import views


urlpatterns = [
    path('cart/add/<int:product_id>', views.add_to_cart, name="cart_add"),
    path('cart/', views.cart_detail, name='cart_detail'),

    path('cart/update/<int:item_id>/', views.update_cart_item, name='cart_update'),

    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='cart_remove'),
]