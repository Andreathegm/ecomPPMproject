from decimal import Decimal,ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

from ecommerce_core import settings
from orders.models import OrderItem, Order

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    if settings.USE_CLOUDINARY:
        image = CloudinaryField('category_image', blank=True, null=True, folder='ecommerce/categories_images/')
    else:
        image = models.ImageField(upload_to='categories_images/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # discounts
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of discount applied to the product (0-100%)"
    )
    discount_start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Start date of the current discount"
    )
    discount_end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="End date of the current discount "
    )
    is_discount_active = models.BooleanField(
        default=False,
        help_text="Activate/deactivate the current discount"
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def get_main_image(self):
        main_image = self.images.filter(is_main=True).first()
        return main_image.image.url if main_image else f'https://placehold.co/300x300/eee/333?text={self.name}'

    @property
    def has_active_discount(self):
        if not self.is_discount_active or self.discount_percentage <= 0:
            return False

        now = timezone.now()

        if self.discount_start_date and self.discount_end_date:
            return self.discount_start_date <= now <= self.discount_end_date
        elif self.discount_start_date:
            return now >= self.discount_start_date
        elif self.discount_end_date:
            return now <= self.discount_end_date

        # If no dates are set, assume the discount is always active
        return True

    @property
    def discounted_price(self):
        if self.has_active_discount:
            discount_amount = self.price * (self.discount_percentage / 100)
            discounted = self.price - discount_amount
            return discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def discount_amount(self):
        if self.has_active_discount:
            return (self.price * (self.discount_percentage / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')

    @property
    def price_display(self):
        return {
            'original_price': self.price,
            'discounted_price': self.discounted_price,
            'discount_amount': self.discount_amount,
            'discount_percentage': self.discount_percentage,
            'has_discount': self.has_active_discount
        }

    @property
    def mean_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return Decimal('0.0')

        total_rating = sum(review.rating for review in reviews)

        average = Decimal(str(total_rating)) / Decimal(str(reviews.count()))
        return average.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    def star_count(self):
        mean_rating = self.mean_rating
        if mean_rating == Decimal('0.0'):
            return 0

        return int(mean_rating.to_integral_value(rounding=ROUND_HALF_UP))

    @property
    def review_count(self):
        return self.reviews.count()



    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='images',
        help_text="product to which this image belongs"
    )
    if settings.USE_CLOUDINARY:
        image = CloudinaryField('product_image', blank=True, null=True, folder='ecommerce/product_images/')
    else:
        image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    is_main = models.BooleanField(
        default=False,
        help_text="indicates if this is the main image for the product"
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="alternative text for the image (SEO friendly)"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', 'uploaded_at']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{'main pic' if self.is_main else 'secondary pic'} – {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Order from which this review originates"
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def clean(self):
        super().clean()
        if not self.user_has_purchased_product():
            raise ValidationError("You can only review products you have purchased.")

    def user_has_purchased_product(self):
        return OrderItem.objects.filter(
            order__user=self.user,
            product=self.product,
            order__status='delivered'
        ).exists()

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
