from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from .form import OrderForm
from .models import Order


class OrderCreateView(LoginRequiredMixin,
                      PermissionRequiredMixin,
                      CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    permission_required = 'orders.add_order'

    def get_success_url(self):
        return reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin,
                      PermissionRequiredMixin,
                      UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    permission_required = 'orders.change_order'
    success_url = reverse_lazy('order_list')


class OrderListView(LoginRequiredMixin,
                    ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('orders.view_order'):
            return qs.order_by('-created_at')
        return qs.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin,
                      DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('orders.view_order'):
            return qs
        return qs.filter(user=self.request.user)


