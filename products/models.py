from django.db import models
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = CloudinaryField('category_image', blank=True, null=True, folder='ecommerce/categories_images/')

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def get_main_image(self):
        main_image = self.images.filter(is_main=True).first()
        return main_image.image.url if main_image else f'https://placehold.co/300x300/eee/333?text={self.name}'

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='images',
        help_text="product to which this image belongs"
    )

    image = CloudinaryField('product_image', blank=True, null=True, folder='ecommerce/product_images/')

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
