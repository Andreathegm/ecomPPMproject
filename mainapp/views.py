from django.shortcuts import render
from django.core.paginator import Paginator
from products.models import Category  # Assumendo che il model Category sia in products.models


def home(request):
    categories = Category.objects.all()[:5]
    context = {
        'categories': categories,
    }
    return render(request, 'main.html', context)
