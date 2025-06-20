from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total_price',)
    fields = ('product', 'quantity', 'price', 'get_total_price')

    def get_total_price(self, obj):
        if obj.pk:
            return f"€{obj.get_total_price():.2f}"
        return "€0.00"
    get_total_price.short_description = 'Total Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'user',
        'status',
        'total_amount',
        'get_total_items',
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
        'order_number',
        'user__username',
        'user__email',
        'shipping_email',
        'shipping_name'
    ]

    readonly_fields = [
        'order_number',
        'created_at',
        'updated_at',
        'subtotal',
        'tax_amount',
        'total_amount',
        'get_total_items',
        'get_order_summary'
    ]

    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'user',
                'status',
                'created_at',
                'updated_at',
                'get_order_summary'
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
        })
    )

    inlines = [OrderItemInline]

    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'

    def get_order_summary(self, obj):
        if obj.pk:
            items = obj.order_items.all()
            if items:
                summary = "<strong>Items in this order:</strong><br>"
                for item in items:
                    summary += f"• {item.quantity}x {item.product.name} - €{item.get_total_price():.2f}<br>"
                return mark_safe(summary)
        return "No items"
    get_order_summary.short_description = 'Order Summary'

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = 'Mark selected orders as processing'

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order_link',
        'product',
        'quantity',
        'price',
        'get_total_price',
        'created_at'
    ]

    list_filter = [
        'created_at',
        'product__category',  # Assuming your Product model has a category field
        'order__status'
    ]

    search_fields = [
        'order__order_number',
        'product__name',
        'order__user__username'
    ]

    readonly_fields = ['get_total_price', 'created_at', 'order_link']

    # Disable add/delete permissions - OrderItems should only be created through checkout
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow delete only if order is still pending
        if obj and obj.order.status == 'pending':
            return True
        return False

    def get_total_price(self, obj):
        # Add safety check to prevent errors
        if obj and obj.quantity and obj.price:
            return f"€{obj.get_total_price():.2f}"
        return "€0.00"
    get_total_price.short_description = 'Total Price'

    def order_link(self, obj):
        if obj and obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "No Order"
    order_link.short_description = 'Order'