from django.shortcuts import render
from products.models import Category  # Assumendo che il model Category sia in products.models


def home(request):
    categories = Category.objects.all()[:5]
    for category in categories:
        print(category.image)
    context = {
        'categories': categories,
    }
    return render(request, 'main.html', context)
