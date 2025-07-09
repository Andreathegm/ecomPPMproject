from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from cart.utils import get_or_create_cart
from cart.models import CartItem
from django.contrib import messages

from products.models import Review
from utils.search import calculate_shipping_cost
from .form import OrderForm
from .models import Order, OrderItem
from decimal import Decimal


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/order_form.html'
    success_url = reverse_lazy('order_history')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        ctx['cart'] = cart
        ctx['cart_items_count'] = cart.items.filter(product__stock__gt=0).count()
        ctx['shipping_cost'] = calculate_shipping_cost()
        ctx['total_amount'] = cart.grand_total + ctx['shipping_cost']
        ctx['discounted_total_plus_shipped'] = cart.discounted_grand_total + ctx['shipping_cost']
        return ctx

    def form_valid(self, form):
        cart = get_or_create_cart(self.request)
        items = cart.items.select_related('product').filter(product__stock__gt=0)
        if not items.exists():
            form.add_error(None, "Impossible to complete the transaction because one of your item is out of stock.")
            return self.form_invalid(form)

        # Salva l'ordine base (shipping + user)
        order = form.save(commit=False)
        order.user = self.request.user
        # Copia i totali dal carrello

        if cart.grand_total == cart.discounted_grand_total:
            order.subtotal      = cart.total
            order.tax_amount    = cart.tax
            order.total_amount  = self.get_context_data()['total_amount']
        elif cart.discounted_grand_total < cart.grand_total:
            order.subtotal      = cart.discounted_total
            order.tax_amount    = cart.discounted_tax
            order.total_amount  = self.get_context_data()['discounted_total_plus_shipped']

        order.shipping_cost = self.get_context_data()['shipping_cost']
        order.save()

        # create OrderItems and update product stock
        for ci in items:
            if ci.discounted_price < ci.unit_price:
                order_price = ci.discounted_price
            else:
                order_price = ci.unit_price
            OrderItem.objects.create(
                order=order,
                product=ci.product,
                quantity=ci.quantity,
                price=order_price,
                product_name=ci.product.name
            )
            ci.product.stock -= ci.quantity
            ci.product.save()

        items_to_delete = list(items)
        for item in items_to_delete:
            item.delete()

        if items.count() == cart.items.count():
            cart.status = cart.Status.COMPLETED
        cart.save()

        return super().form_valid(form)


@login_required
def order_confirm_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/confirmation.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items__product').order_by('-created_at')
    ids = set()

    for order in orders:
        product_ids = order.order_items.values_list('product_id', flat=True)
        ids.update(product_ids)

    reviews = Review.objects.filter(product_id__in=ids).select_related('product')
    review_map = {review.product.id: review for review in reviews}


    # Crea un dizionario semplice: product_id -> review
    context = {
        'orders': orders,
        'reviews': review_map,

    }
    return render(request, 'order/order_history.html', context)


###########STORE MANAGER VIEWS FOR MANAGING ORDERS###########
@login_required
@permission_required('orders.view_all_orders', raise_exception=True)
def order_management_view(request):
    orders = Order.objects.select_related('user').prefetch_related('order_items__product')
    status_choices = Order._meta.get_field('status').choices
    return render(request, 'store_manager/manageorders.html', {
        'orders': orders,
        'status_choices': status_choices,
    })


@require_POST
@login_required
@permission_required('orders.change_all_orders', raise_exception=True)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # # Se non sei il proprietario, verifica il permesso custom "change_all_orders"
    # if order.user != request.user and not request.user.has_perm('orders.change_all_orders'):
    #     messages.error(request, "Non hai il permesso per modificare questo ordine.")
    #     return redirect('order_management')

    new_status = request.POST.get('status')
    valid_statuses = dict(Order._meta.get_field('status').choices)
    if new_status not in valid_statuses:
        messages.error(request, "Not a valid state.")
    else:
        order.status = new_status
        order.save()
        messages.success(request, f"State updated successfully, new state --> “{valid_statuses[new_status]}”.")
    return redirect('order_management_list')


@require_POST
@login_required
@permission_required('orders.delete_all_orders', raise_exception=True)
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'shipped':
        messages.error(request, "You can't eliminate an already shipped order.")
    else:
        order.delete()
        messages.success(request, "Order eliminated successfully.")
    return redirect('order_management_list')
