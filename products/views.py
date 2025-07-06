from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from products.forms import ProductForm, CreateImageFormSet, EditImageFormSet, CategoryForm
from products.models import Category, Product
from utils.search import get_filtered_products


####### category and product views (for customer) ########
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
    p_images = list(product.images.all())
    images = [img.image for img in p_images]# Exclude the main image if needed
    # Supponendo che il modello Product abbia un campo images
    context = {
        'product': product,
        'p_images': images,
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

        if self.request.GET.get('search'):
            qs = get_filtered_products(self, qs)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Serve per la lista delle categorie nel filtro laterale
        ctx['category_list'] = Category.objects.all()

        # Per ripopolare i controlli UI con i valori correnti
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_max_price'] = self.request.GET.get('max_price', '')
        ctx['selected_order'] = self.request.GET.get('order', '')

        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['get_params'] = params.urlencode()

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
        return get_filtered_products(self)

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


######### PRODUCT MANAGEMENT VIEWS #########
@permission_required('products.add_product', raise_exception=True)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = CreateImageFormSet(request.POST, request.FILES, prefix='images')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # 1) Salvo il Product con slug
                    product = form.save(commit=False)
                    base_slug = slugify(product.name)
                    slug = base_slug
                    counter = 1
                    while Product.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    product.slug = slug
                    product.save()

                    # 2) Salvo le immagini
                    formset.instance = product

                    # Conta quante immagini principali abbiamo
                    main_image_count = 0

                    for image_form in formset:
                        if image_form.cleaned_data and not image_form.cleaned_data.get('DELETE', False):
                            img = image_form.cleaned_data.get('image')
                            if img:  # Solo se c'è un'immagine
                                # Salva l'immagine
                                pi = image_form.save(commit=False)
                                pi.product = product

                                # Gestisci is_main - solo la prima può essere main
                                if pi.is_main:
                                    main_image_count += 1
                                    if main_image_count > 1:
                                        pi.is_main = False

                                # Imposta alt_text
                                if pi.is_main:
                                    pi.alt_text = f"Main image of {product.name}"
                                else:
                                    pi.alt_text = f"Secondary image of {product.name}"

                                pi.save()

                    messages.success(request, 'Product created successfully!')
                    return redirect('manage_catalog')

            except Exception as e:
                messages.error(request, f'Error saving product: {e}')
                print(f"Exception details: {e}")  # Per debug
        else:
            # Debug degli errori
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    print(f"Form {i} errors: {form_errors}")
    else:
        form = ProductForm()
        formset = CreateImageFormSet(prefix='images')

    return render(request, 'store_manager/product_form_def.html', {
        'product_form': form,
        'formset': formset,
        'title': 'Add Product',
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
            for i, f in enumerate(formset):
                print(f.cleaned_data)
            try:
                with transaction.atomic():

                    # 1) Salva o aggiorna il prodotto
                    updated_product = form.save()

                    main_assigned = False  # flag per tenere traccia

                    # 2) Gestione di ogni sotto-form immagine
                    for image_form in formset:
                        cd = image_form.cleaned_data
                        instance = image_form.instance

                        # A) Cancellazione
                        if cd.get('DELETE', False) and instance.pk:
                            if instance.image:
                                instance.image.delete(save=False)
                            instance.delete()
                            continue

                        # B) Nuovo upload o modifica
                        if cd.get('image') or instance.pk:
                            pi = image_form.save(commit=False)
                            pi.product = updated_product

                            # Se l’utente ha marcato questa immagine come main
                            if pi.is_main:
                                main_assigned = True
                                # rimuove il flag di main dalle altre immagini
                                (updated_product.images
                                 .exclude(pk=pi.pk)
                                 .update(is_main=False))

                            # Popola alt_text solo se mancante
                            if not pi.alt_text:
                                pi.alt_text = (
                                    f"Main image of {updated_product.name}"
                                    if pi.is_main
                                    else f"Secondary image of {updated_product.name}"
                                )

                            pi.save()

                    # 3) Se non c’è nessuna main, promuovi la prima disponibile
                    if not main_assigned:
                        first_img = updated_product.images.first()
                        if first_img:
                            first_img.is_main = True
                            first_img.save()

                    messages.success(request, 'Prodotto aggiornato con successo!')
                    return redirect('manage_catalog')

            except Exception as e:
                messages.error(request, f'Errore durante l\'aggiornamento del prodotto: {e}')
                print(f"Exception in modify_product: {e}")
                # Log più dettagliato per debug
                import traceback
                traceback.print_exc()
        else:
            # Debug degli errori
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    print(f"Image form {i} errors: {form_errors}")

            # Mostra errori all'utente
            if form.errors:
                messages.error(request, 'Ci sono errori nel form del prodotto.')
            if formset.errors:
                messages.error(request, 'Ci sono errori nelle immagini.')

    else:
        form = ProductForm(instance=product)
        formset = ImageFormSet(instance=product, prefix='images')

    return render(request, 'store_manager/product_form_def.html', {
        'product_form': form,
        'formset': formset,
        'title': f'Modifica Prodotto: {product.name}',
        'is_edit': True,
        'product': product,  # Aggiungi questo per debug
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


######CATEGORY MANAGEMENT VIEWS######

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/category_formdef.html'
    permission_required = 'products.add_category'
    success_url = reverse_lazy('manage_catalog')

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        messages.success(self.request, f'Category "{form.instance.name}" added successfully.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/category_formdef.html'
    permission_required = 'products.change_category'
    success_url = reverse_lazy('manage_catalog')

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    permission_required = 'products.delete_category'
    success_url = reverse_lazy('manage_catalog')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f'Category "{category.name}" eliminated successfully.')
        return super().delete(request, *args, **kwargs)
