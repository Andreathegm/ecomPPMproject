# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, Product, ProductImage


# Inline per gestire le immagini direttamente nel Product
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'alt_text', 'is_main', 'uploaded_at')
    readonly_fields = ('image_preview', 'uploaded_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 80px; max-height: 80px; border-radius: 4px;"/>',
                obj.image.url
            )
        return "Nessuna immagine"
    image_preview.short_description = "Anteprima"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available', 'main_image_preview')
    list_filter = ('available', 'category', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    def main_image_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px;"/>',
                main_image.image.url
            )
        return "Nessuna immagine"
    main_image_preview.short_description = "Immagine principale"


# Admin per ProductImage (se vuoi gestirle anche separatamente)
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'image_name', 'is_main', 'alt_text', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at', 'product__category')
    search_fields = ('product__name', 'alt_text')
    ordering = ('-uploaded_at',)

    fields = ('product', 'image_preview', 'image', 'alt_text', 'is_main', 'uploaded_at')
    readonly_fields = ('image_preview', 'uploaded_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"/>',
                obj.image.url
            )
        return "Nessuna immagine"
    image_preview.short_description = "Anteprima immagine"

    def image_name(self, obj):
        if obj.image:
            return obj.image.name.split('/')[-1]  # Solo il nome del file
        return "Nessun file"
    image_name.short_description = "Nome file"