# orders/urls.py
from django.urls import path
from .views import OrderCreateView, order_confirm_view, order_history_view

urlpatterns = [
    # 1) Mostra il form di checkout (GET) e processa order + cart (POST)
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),

    # 2) Pagina di conferma dell’ordine appena creato
    path('orders/<uuid:order_id>/confirm/', order_confirm_view, name='order_confirm'),

    # 3) Storico ordini utente
    path('orders/history/', order_history_view, name='order_history'),
]


