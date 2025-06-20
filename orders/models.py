from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Shipping Information
    shipping_name = models.CharField(max_length=100)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Italy')

    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Payment info (basic)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_total_items(self):
        """Return total number of items in this order"""
        return sum(item.quantity for item in self.order_items.all())

    def calculate_totals(self):
        """Calculate and update order totals"""
        self.subtotal = sum(item.get_total_price() for item in self.order_items.all())
        # Simple tax calculation (22% VAT for Italy)
        self.tax_amount = self.subtotal * Decimal('0.22')
        # Simple shipping calculation
        if self.subtotal < Decimal('50.00'):
            self.shipping_cost = Decimal('5.99')
        else:
            self.shipping_cost = Decimal('0.00')  # Free shipping over 50€

        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)  # Assuming your product app is named 'products'
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        # Ensure same product can't be added twice to same order
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.order_number}"

    def get_total_price(self):
        """Return total price for this order item"""
        # Add safety checks to prevent errors
        if self.quantity and self.price:
            return self.quantity * self.price
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        # Set price from product if not already set
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

        # Update order totals when order item is saved
        self.order.calculate_totals()