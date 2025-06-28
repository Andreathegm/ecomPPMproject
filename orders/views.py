from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from cart.utils import get_or_create_cart
from cart.models import CartItem
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
        return ctx

    def form_valid(self, form):
        cart = get_or_create_cart(self.request)
        items = cart.items.select_related('product')
        if not items.exists():
            form.add_error(None, "your cart is empty.")
            return self.form_invalid(form)

        # Salva l'ordine base (shipping + user)
        order = form.save(commit=False)
        order.user = self.request.user
        # Copia i totali dal carrello
        order.subtotal      = cart.total
        order.tax_amount    = cart.tax
        # se hai shipping cost fisso: order.shipping_cost = cart.tax*0 ecc.
        order.shipping_cost = Decimal('5.00')  # o un calcolo dinamico
        order.total_amount  = cart.grand_total
        order.save()

        # Crea le righe ordine
        for ci in items:
            OrderItem.objects.create(
                order=order,
                product=ci.product,
                quantity=ci.quantity,
                price=ci.unit_price
            )

        # Svuota il carrello
        items.delete()
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
    return render(request, 'order/order_history.html', {'orders': orders})
