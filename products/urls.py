from django.urls import path
from . import views

urlpatterns = [
    path('<slug:category_slug>/', views.category_view, name='category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
]