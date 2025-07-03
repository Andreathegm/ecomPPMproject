# orders/urls.py
from django.urls import path
from .views import OrderCreateView, order_confirm_view, order_history_view, update_order_status, delete_order, \
    order_management_view

urlpatterns = [
    # 1) Mostra il form di checkout (GET) e processa order + cart (POST)
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),

    # 2) Pagina di conferma dell’ordine appena creato
    path('orders/<uuid:order_id>/confirm/', order_confirm_view, name='order_confirm'),

    # 3) Storico ordini utente
    path('orders/history/', order_history_view, name='order_history'),

    path('orders/storemanagers/orderlist', order_management_view, name='order_management_list'),
    path('orders/storemanagers/<uuid:order_id>/update/', update_order_status, name='order_update'),
    path('orders/storemanagers/<uuid:order_id>/delete/', delete_order, name='order_delete'),
]


