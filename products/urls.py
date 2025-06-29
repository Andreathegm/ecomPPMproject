from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('<slug:category_slug>/', views.category_view, name='category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),

    path('storemanagers/products/add/', views.add_product, name='add_product'),

]