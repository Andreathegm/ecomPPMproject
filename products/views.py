from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from orders.models import Order
from products.forms import ProductForm, CreateImageFormSet, EditImageFormSet, CategoryForm
from products.models import Category, Product, Review
from utils.search import get_filtered_products, filter_discount, get_filtered_products_request


####### category and product views (for customer) ########
def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, available=True)
    ###so that i am sure this GET is from the filter form
    if request.method == 'GET' and request.GET.get('min_rating'):
        products = get_filtered_products_request(request, products)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    context = {
        'category': category,
        'products': paginator.get_page(page_number),
        'min_rating': request.GET.get('min_rating', ''),
        'selected_max_price': request.GET.get('max_price', ''),
        'selected_order': request.GET.get('order', ''),
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

        if self.request.GET.get('discount') in ['1', 'true', 'True', 'yes']:
            qs = filter_discount(qs)


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

        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            try:
                min_rating = int(min_rating)
                products = [
                    product for product in qs
                    if product.mean_rating is not None and product.mean_rating >= min_rating
                ]
                qs = products
            except (ValueError, TypeError):
                pass

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
    paginate_by = 9

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

                    # 1) Save or update the Product
                    updated_product = form.save()

                    main_assigned = False  # flag to check if a main image is assigned

                    # 2) Manage every image in the formset
                    for image_form in formset:
                        cd = image_form.cleaned_data
                        instance = image_form.instance

                        # A) Cancellation
                        if cd.get('DELETE', False) and instance.pk:
                            if instance.image:
                                instance.image.delete(save=False)
                            instance.delete()
                            continue

                        # B) new upload or modify
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

                    messages.success(request, 'Product updated successfully!')
                    return redirect('manage_catalog')

            except Exception as e:
                messages.error(request, f'Error updating the product: {e}')
                print(f"Exception in modify_product: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    print(f"Image form {i} errors: {form_errors}")

            if form.errors:
                messages.error(request, 'Error in product form modifying products.')
            if formset.errors:
                messages.error(request, 'Error in product form modifying images.')

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

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        try:
            product.delete()
            messages.success(request, f'Product "{product_name}" eliminated_successfully!')
        except Exception as e:
            messages.error(request, f'Error during elimination of product {str(e)}')

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

####PRODUCT REVIEWS VIEWS####


@login_required
@require_POST
def create_review(request):
    product_id = request.POST.get('product_id')
    order_id = request.POST.get('order_id')
    rating = request.POST.get('rating')
    review_text = request.POST.get('review_text')

    try:
        product = get_object_or_404(Product, id=product_id)
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Verifica che l'ordine sia stato consegnato
        if order.status != 'delivered':
            messages.error(request, "You can only review products from delivered orders.")
            return redirect('order_history')

        # Verifica che il prodotto sia nell'ordine
        if not order.order_items.filter(product=product).exists():
            messages.error(request, "You can only review products you have purchased.")
            return redirect('order_history')

        # Crea o aggiorna la recensione
        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'order': order,
                'rating': int(rating),
                'review_text': review_text
            }
        )

        # Valida il modello
        review.full_clean()

        if created:
            messages.success(request, "Review submitted successfully!")
        else:
            messages.success(request, "Review updated successfully!")

    except ValidationError as e:
        messages.error(request, str(e))
    except ValueError:
        messages.error(request, "Invalid rating value.")
    except Exception as e:
        messages.error(request, "An error occurred while saving your review.")

    return redirect('order_history')


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted successfully!")

    return redirect('order_history')