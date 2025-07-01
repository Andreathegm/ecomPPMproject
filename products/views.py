from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView

from products.forms import ProductForm, CreateImageFormSet, EditImageFormSet, CategoryForm
from products.models import Category, Product


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
    context_object_name = 'products'  # In template: use 'products' to iterate
    paginate_by = 12  # Number of products per page

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
        if order == '1':  # Prezzo crescente
            qs = qs.order_by('price')
        elif order == '2':  # Prezzo decrescente
            qs = qs.order_by('-price')
        else:  # Default o “Più recenti”
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


@method_decorator([login_required, permission_required('products.change_product', raise_exception=True)],
                  name='dispatch')
class ManageCatalogView(ListView):
    """
    View per la gestione del catalogo da parte dello store manager.
    Mostra categorie e prodotti con opzioni di gestione.
    """
    model = Product
    template_name = 'store_manager/managecatolog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """
        Restituisce queryset filtrato per ricerca, categoria e prezzo.
        Include anche i prodotti non disponibili per la gestione.
        """
        qs = Product.objects.all()  # Include anche prodotti non disponibili

        # ---- Filtro per ricerca ----
        search_query = self.request.GET.get('search')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

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
        if order == '1':  # Prezzo crescente
            qs = qs.order_by('price')
        elif order == '2':  # Prezzo decrescente
            qs = qs.order_by('-price')
        elif order == '3':  # Più recenti
            qs = qs.order_by('-created_at')
        else:  # Default
            qs = qs.order_by('name')

        return qs

    def get_context_data(self, **kwargs):
        """
        Aggiunge categorie e parametri di ricerca al context.
        """
        ctx = super().get_context_data(**kwargs)

        # Lista delle categorie per il filtro laterale
        ctx['category_list'] = Category.objects.all()

        # Categorie per la sezione superiore (con filtro di ricerca se applicabile)
        categories = Category.objects.all()
        search_query = self.request.GET.get('search')
        if search_query:
            categories = categories.filter(name__icontains=search_query)
        ctx['categories'] = categories

        # Per ripopolare i controlli UI con i valori correnti
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_max_price'] = self.request.GET.get('max_price', '')
        ctx['selected_order'] = self.request.GET.get('order', '')
        ctx['search_query'] = search_query or ''

        return ctx


############ CATEGORY MANAGEMENT VIEWS ############

# Aggiungi questa view al tuo views.py esistente

@method_decorator([login_required, permission_required('products.change_product', raise_exception=True)], name='dispatch')
class ManageCatalogView(ListView):
    """
    View per la gestione del catalogo da parte dello store manager.
    Mostra categorie e prodotti con opzioni di gestione.
    """
    model = Product
    template_name = 'store_manager/managecatolog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """
        Restituisce queryset filtrato per ricerca, categoria e prezzo.
        Include anche i prodotti non disponibili per la gestione.
        """
        qs = Product.objects.all()  # Include anche prodotti non disponibili

        # ---- Filtro per ricerca ----
        search_query = self.request.GET.get('search')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

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
        elif order == '3':      # Più recenti
            qs = qs.order_by('-created_at')
        else:                   # Default
            qs = qs.order_by('name')

        return qs

    def get_context_data(self, **kwargs):
        """
        Aggiunge categorie e parametri di ricerca al context.
        """
        ctx = super().get_context_data(**kwargs)

        # Lista delle categorie per il filtro laterale
        ctx['category_list'] = Category.objects.all()

        # Categorie per la sezione superiore (con filtro di ricerca se applicabile)
        categories = Category.objects.all()
        search_query = self.request.GET.get('search')
        if search_query:
            categories = categories.filter(name__icontains=search_query)
        ctx['categories'] = categories

        # Per ripopolare i controlli UI con i valori correnti
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_max_price'] = self.request.GET.get('max_price', '')
        ctx['selected_order'] = self.request.GET.get('order', '')
        ctx['search_query'] = search_query or ''

        return ctx


@permission_required('products.add_product', raise_exception=True)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = CreateImageFormSet(request.POST, request.FILES, prefix='images')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save()
                formset.instance = product
                formset.save()
            messages.success(request, 'Prodotto creato!')
            return redirect('manage_catalog')
    else:
        form = ProductForm()
        formset = CreateImageFormSet(prefix='images')

    return render(request, 'store_manager/add_product.html', {
        'product_form': form,
        'formset': formset,
        'title': 'Aggiungi Prodotto',
        'is_edit': False,
    })


@permission_required('products.change_product', raise_exception=True)
def modify_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    ImageFormSet = EditImageFormSet

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ImageFormSet(request.POST, request.FILES, instance=product, prefix='images')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save()
                formset.save()
            messages.success(request, 'Prodotto aggiornato!')
            return redirect('manage_catalog')
    else:
        form = ProductForm(instance=product)
        formset = ImageFormSet(instance=product, prefix='images')

    return render(request, 'store_manager/add_product.html', {
        'product_form': form,
        'formset': formset,
        'title': f'Modifica Prodotto: {product.name}',
        'is_edit': True,
    })


@permission_required('products.delete_product', raise_exception=True)
def delete_product(request, product_id):
    """
    View per eliminare un prodotto con conferma diretta.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        try:
            product.delete()
            messages.success(request, f'Prodotto "{product_name}" eliminato con successo!')
        except Exception as e:
            messages.error(request, f'Errore durante l\'eliminazione del prodotto: {str(e)}')

    return redirect('manage_catalog')


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/category_form.html'
    permission_required = 'products.add_category'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Categoria "{form.instance.name}" creata con successo.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/category_form.html'
    permission_required = 'products.change_category'
    success_url = reverse_lazy('manage_catalog')

    def form_valid(self, form):
        messages.success(self.request, f'Categoria "{form.instance.name}" aggiornata con successo.')
        return super().form_valid(form)
