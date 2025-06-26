from django.urls import path
from .views import (
    OrderCreateView, OrderUpdateView,
    OrderListView, OrderDetailView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('new/', OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/edit/', OrderUpdateView.as_view(), name='order_update'),
]
