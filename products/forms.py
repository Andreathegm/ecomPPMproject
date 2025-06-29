from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'description',
            'price', 'stock', 'available',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crispy helper senza Submit → unico bottone in template
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            'category', 'name', 'slug', 'description',
            'price', 'stock', 'available',
        )


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'style': 'display: none;'  # Nascosto perché usiamo l'interfaccia custom
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Testo alternativo per l\'immagine',
                'style': 'display: none;'  # Gestito dal JavaScript
            }),
            'is_main': forms.CheckboxInput(attrs={
                'style': 'display: none;'  # Gestito automaticamente
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rimuovi le label perché usiamo un'interfaccia custom
        for field in self.fields:
            self.fields[field].label = ''
            self.fields[field].help_text = ''


# Formset ottimizzato: inizia con 10 form vuoti (1 principale + 9 secondarie)
# ma solo 1 viene mostrato inizialmente
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=10,  # Creiamo 10 form vuoti
    max_num=10,  # Massimo 10 immagini totali
    can_delete=True,
    validate_max=True,
    min_num=0,  # Minimo 0 immagini (opzionale)
    validate_min=False,  # Non forzare il minimo
)