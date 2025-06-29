from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from cart.models import Cart
from products.forms import ProductForm, ProductImageFormSet
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


class ProductListView(ListView):
    """
    Generic ListView that displays all available products,
    paginated, ordered by creation date descending.
    """
    model = Product
    template_name = 'products/product_listing.html'  # Default: products/product_list.html
    context_object_name = 'products'              # In template: use 'products' to iterate
    paginate_by = 12                           # Number of products per page

    def get_queryset(self):
        qs = Product.objects.filter(available=True)

        # ---- Filtro per categoria ----
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # ---- Filtro per prezzo massimo ----
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                max_price = float(max_price)
                qs = qs.filter(price__lte=max_price)
            except ValueError:
                pass

        # ---- Ordinamento ----
        order = self.request.GET.get('order')
        if order == '1':        # Prezzo crescente
            qs = qs.order_by('price')
        elif order == '2':      # Prezzo decrescente
            qs = qs.order_by('-price')
        else:                   # Default o “Più recenti”
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Serve per la lista delle categorie nel filtro laterale
        ctx['category_list'] = Category.objects.all()

        # Per ripopolare i controlli UI con i valori correnti
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_max_price'] = self.request.GET.get('max_price', '')
        ctx['selected_order'] = self.request.GET.get('order', '')

        return ctx


@permission_required('products.add_product', raise_exception=True)
def add_product(request):
    if request.method == 'POST':
        form    = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, "Prodotto creato con successo!")
            return redirect('main')
    else:
        form    = ProductForm()
        formset = ProductImageFormSet()

    return render(request, 'store_manager/add_product.html', {
        'form': form,
        'formset': formset
    })


def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        print("Form valid:", form.is_valid())
        print("Formset valid:", formset.is_valid())

        if form.errors:
            print("Form errors:", form.errors)
        if formset.errors:
            print("Formset errors:", formset.errors)

        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            return redirect('success_url')
    # ... resto del codice