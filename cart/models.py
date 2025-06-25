from django.db import models

from products.models import Product

# Create your models here.
"""
cart/models.py

Definizione dei modelli del dominio "carrello": Cart e CartItem.
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum, DecimalField


class TimestampedModel(models.Model):
    """
    Modello astratto che aggiunge campi di creazione e modifica.
    """
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora di creazione del record"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="Data e ora dell'ultima modifica del record"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Cart(TimestampedModel):
    """
    Rappresenta un carrello associato a un utente.
    """
    class Status(models.TextChoices):
        OPEN = 'open', 'Aperto'
        COMPLETED = 'completed', 'Completato'
        CANCELLED = 'cancelled', 'Annullato'

    cart_id: models.AutoField = models.CharField(max_length=250, blank=True)
    #
    # user: models.ForeignKey = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='carts',
    #     help_text="Utente proprietario del carrello"
    # )
    status: models.CharField = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        help_text="Stato corrente del carrello"
    )

    def __str__(self) -> str:
        return f"Cart(id={self.pk}, status={self.status})"

    @property
    def total(self) -> Decimal:
        """
        Calcola il totale sommando quantity * unit_price di ogni CartItem.
        """
        aggregate = self.items.aggregate(
            total=Sum(
                F('quantity') * F('unit_price'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        return (aggregate['total'] or Decimal('0.00')).quantize(Decimal('0.01'))

    @property
    def tax(self) -> Decimal:
        """
        Calcola le tasse applicate al totale del carrello.
        Per ora, ritorna un placeholder del 2% del totale.
        """
        return (self.total * Decimal('0.02')).quantize(Decimal('0.01'))

    @property
    def grand_total(self) -> Decimal:
        """
        Calcola il totale comprensivo di eventuali tasse o sconti.
        Per ora, ritorna lo stesso valore di total.
        """
        # Implementa qui logica per tasse/sconti se necessario
        return (self.total + self.tax)  # Placeholder per tasse/sconti


class CartItem(TimestampedModel):
    """
    Rappresenta una voce di prodotto all'interno di un carrello.
    """
    cart: models.ForeignKey = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Carrello di appartenenza"
    )
    product: models.ForeignKey = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='cart_items',
        help_text="Prodotto aggiunto al carrello"
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantità richiesta, minimo 1"
    )
    unit_price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Prezzo unitario al momento dell'aggiunta"
    )

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-created_at']
        verbose_name = 'Voce Carrello'
        verbose_name_plural = 'Voci Carrello'

    def __str__(self) -> str:
        return f"CartItem(cart_id={self.cart_id}, product={self.product}, qty={self.quantity})"

    @property
    def subtotal(self) -> Decimal:
        """
        Restituisce prezzo unitario moltiplicato per quantità.
        """
        return self.unit_price * self.quantity

