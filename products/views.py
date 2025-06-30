from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from cart.models import Cart
from products.forms import ProductForm, ProductImageFormSet, ProductImageFormSetHelper
from products.models import Category, Product, ProductImage


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
    """
    View per aggiungere un nuovo prodotto con le relative immagini.
    Protetta dal permesso 'add_product'.
    """
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if product_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Salva il prodotto
                    product = product_form.save()

                    # Salva le immagini
                    formset.instance = product
                    instances = formset.save()

                    # Verifica che ci sia almeno un'immagine principale
                    main_images = [img for img in instances if img.is_main]
                    if not main_images and instances:
                        # Se non c'è un'immagine principale, imposta la prima come principale
                        instances[0].is_main = True
                        instances[0].save()
                    elif len(main_images) > 1:
                        # Se ci sono più immagini principali, mantieni solo la prima
                        for img in main_images[1:]:
                            img.is_main = False
                            img.save()

                messages.success(
                    request,
                    f'Prodotto "{product.name}" aggiunto con successo!'
                )
                return redirect('product_detail', product_slug=product.slug)
                # Oppure redirect alla lista prodotti: return redirect('product_list')

            except Exception as e:
                messages.error(
                    request,
                    f'Errore durante il salvataggio del prodotto: {str(e)}'
                )
        else:
            # Gestione errori di validazione
            if not product_form.is_valid():
                messages.error(request, 'Errori nel form del prodotto. Controlla i campi evidenziati.')
            if not formset.is_valid():
                messages.error(request, 'Errori nelle immagini. Controlla i campi evidenziati.')

    else:
        # GET request - mostra form vuoti
        product_form = ProductForm()
        formset = ProductImageFormSet()

    # Helper per il formset
    formset_helper = ProductImageFormSetHelper()

    context = {
        'product_form': product_form,
        'formset': formset,
        'formset_helper': formset_helper,
        'title': 'Aggiungi Nuovo Prodotto',
    }

    return render(request, 'store_manager/add_product.html', context)