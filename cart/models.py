from django.db import models
from products.models import Product
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum, DecimalField


class TimestampedModel(models.Model):
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of record creation"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="Date and time of last record update"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Cart(TimestampedModel):

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    cart_id = models.CharField(max_length=250, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
        help_text="User associated with the cart"
    )

    status: models.CharField = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        help_text="current status of the cart"
    )

    def __str__(self) -> str:
        return f"Cart(id={self.pk}, status={self.status})"

    @property
    def total(self) -> Decimal:
        """
        Calcola il totale sommando quantity * unit_price di ogni CartItem.
        """
        aggregate = self.items.filter(product__stock__gt=0).aggregate(
            total=Sum(
                F('quantity') * F('unit_price'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        return (aggregate['total'] or Decimal('0.00')).quantize(Decimal('0.01'))

    @property
    def tax(self) -> Decimal:
        return (self.total * Decimal('0.02')).quantize(Decimal('0.01'))

    @property
    def grand_total(self) -> Decimal:
        return (self.total + self.tax)  # Placeholder per tasse/sconti

    @property
    def discounted_total(self) -> Decimal:
        total = Decimal('0.00')

        for item in self.items.select_related('product'):
            product = item.product
            unit_price = (
                product.discounted_price if product.has_active_discount else item.unit_price
            )
            total += unit_price * item.quantity

        return total.quantize(Decimal('0.01'))

    @property
    def discounted_tax(self) -> Decimal:

        return (self.discounted_total * Decimal('0.02')).quantize(Decimal('0.01'))

    @property
    def discounted_grand_total(self) -> Decimal:

        return (self.discounted_total + self.discounted_tax).quantize(Decimal('0.01'))

    @property
    def savings(self):
        return self.grand_total - self.discounted_grand_total


class CartItem(TimestampedModel):

    cart: models.ForeignKey = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Cart of which this item is part"
    )
    product: models.ForeignKey = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        help_text="Product associated with this cart item"
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="minimum quantity is 1, default is 1"
    )
    unit_price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="unit price of the product at the time of adding to cart"
    )

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-created_at']
        verbose_name = 'CartItem'
        verbose_name_plural = 'CartItems'

    def __str__(self) -> str:
        return f"CartItem(cart_id={self.cart_id}, product={self.product}, qty={self.quantity})"

    @property
    def subtotal(self) -> Decimal:

        return self.unit_price * self.quantity

    @property
    def discounted_subtotal(self) -> Decimal:
        if self.product.has_active_discount:
            total = self.product.discounted_price * self.quantity
        else:
            total = self.subtotal
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def discounted_price(self) -> Decimal:
        if self.product.has_active_discount:
            return self.product.discounted_price
        return self.unit_price


