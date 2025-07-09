import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    # Shipping
    shipping_name        = models.CharField(max_length=100)
    shipping_email       = models.EmailField()
    shipping_phone       = models.CharField(max_length=20, blank=True)
    shipping_address     = models.TextField()
    shipping_city        = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country     = models.CharField(max_length=100, default='Italy')

    # Totals
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.order_items.all())

    def calculate_totals(self):
        subtotal = sum(item.total_price for item in self.order_items.all())
        tax      = subtotal * Decimal('0.22')
        shipping = Decimal('5.99') if subtotal < Decimal('50.00') else Decimal('0.00')
        total    = subtotal + tax + shipping

        Order.objects.filter(pk=self.pk).update(
            subtotal=subtotal,
            tax_amount=tax,
            shipping_cost=shipping,
            total_amount=total
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_name = models.CharField(max_length=150, blank=True)
    product = models.ForeignKey('products.Product', null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return (self.quantity * self.price) if self.quantity and self.price else Decimal('0.00')

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.calculate_totals()
