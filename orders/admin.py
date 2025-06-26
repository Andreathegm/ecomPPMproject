from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price_display',)
    fields = ('product', 'quantity', 'price', 'total_price_display')

    def total_price_display(self, obj):
        if obj.pk:
            return f"€{obj.total_price:.2f}"
        return "€0.00"
    total_price_display.short_description = 'Total Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'status',
        'total_amount',
        'total_items',
        'is_paid',
        'created_at'
    ]
    list_filter = [
        'status',
        'is_paid',
        'created_at',
        'shipping_country'
    ]
    search_fields = [
        'id',
        'user__username',
        'user__email',
        'shipping_email',
        'shipping_name'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'subtotal',
        'tax_amount',
        'shipping_cost',
        'total_amount',
        'total_items',
        'order_summary'
    ]
    fieldsets = (
        ('Order Information', {
            'fields': (
                'id',
                'user',
                'status',
                'created_at',
                'updated_at',
                'order_summary'
            )
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_name',
                'shipping_email',
                'shipping_phone',
                'shipping_address',
                'shipping_city',
                'shipping_postal_code',
                'shipping_country'
            )
        }),
        ('Payment & Totals', {
            'fields': (
                'is_paid',
                'payment_method',
                'subtotal',
                'shipping_cost',
                'tax_amount',
                'total_amount'
            )
        }),
    )
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'

    def order_summary(self, obj):
        items = obj.order_items.all()
        if not items:
            return "No items"
        html = ["<strong>Items in this order:</strong><ul style='margin:0; padding-left:1rem;'>"]
        for item in items:
            html.append(f"<li>{item.quantity}× {item.product.name} — €{item.total_price:.2f}</li>")
        html.append("</ul>")
        return mark_safe(''.join(html))
    order_summary.short_description = 'Order Summary'

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = 'Mark selected orders as processing'

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order_link',
        'product',
        'quantity',
        'price',
        'total_price_display',
        'created_at'
    ]
    list_filter = [
        'created_at',
        'product__category',
        'order__status'
    ]
    search_fields = [
        'order__id',
        'product__name',
        'order__user__username'
    ]
    readonly_fields = [
        'total_price_display',
        'created_at',
        'order_link'
    ]

    def has_add_permission(self, request):
        # Gli OrderItem si creano solo via checkout, non da Admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Permetti delete solo se l'ordine è ancora pending
        return bool(obj and obj.order.status == 'pending')

    def total_price_display(self, obj):
        return f"€{obj.total_price:.2f}" if obj else "€0.00"
    total_price_display.short_description = 'Total Price'

    def order_link(self, obj):
        if obj and obj.order_id:
            url = reverse('admin:orders_order_change', args=[obj.order_id])
            return format_html('<a href="{}">Order {}</a>', url, obj.order_id)
        return "No Order"
    order_link.short_description = 'Order'
