from django.urls import path
from . import views
from .views import CategoryCreateView, CategoryUpdateView, CategoryDeleteView

urlpatterns = [
    path('manage/', views.ManageCatalogView.as_view(), name='manage_catalog'),

    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('<slug:category_slug>/', views.category_view, name='category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),


    path('product/reviews/create/', views.create_review, name='create_review'),
    path('product/reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    path('storemanagers/products/add/', views.add_product, name='add_product'),


    # Gestione prodotti
    path('product/<int:product_id>/modify/', views.modify_product, name='modify_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    # Gestione categorie
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),

    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

]

