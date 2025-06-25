from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from products.models import Category, Product


# Create your views here.
def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, available=True)
    paginator = Paginator(products, 8)  # Show 10 products per page
    page_number = request.GET.get('page')
    context = {
        'category': category,
        'products': paginator.get_page(page_number),
    }
    return render(request, 'products/category.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, available=True)
    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)