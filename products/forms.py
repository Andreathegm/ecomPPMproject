# store_manager/forms.py

from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, HTML, Field
from django.utils.text import slugify
from .models import Product, ProductImage, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'class':'form-control', 'rows':4}),
            'price':       forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'stock':       forms.NumberInput(attrs={'class':'form-control'}),
            'name':        forms.TextInput(attrs={'class':'form-control'}),
            'slug':        forms.TextInput(attrs={'class':'form-control'}),
            'available':   forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'category':    forms.Select(attrs={'class':'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"

    # Crispy layout
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Row(
                    Column('category', css_class='col-md-6 mb-3'),
                    Column('available', css_class='col-md-6 mb-3'),
                ),
                Row(
                    Column('name', css_class='col-md-6 mb-3'),
                    Column('slug', css_class='col-md-6 mb-3'),
                ),
                Row(
                    Column('description', css_class='col-12 mb-3'),
                ),
                Row(
                    Column('price', css_class='col-md-6 mb-3'),
                    Column('stock', css_class='col-md-6 mb-3'),
                ),
                css_class='card-body'
            )
        )


class ProductImageForm(forms.ModelForm):
    existing_image = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ProductImage
        fields = ['existing_image', 'image', 'alt_text', 'is_main']
        widgets = {
            'image':     forms.ClearableFileInput(attrs={'class':'form-control'}),
            'alt_text':  forms.TextInput(attrs={'class':'form-control'}),
            'is_main':   forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

    # Se istanza esistente, popola existing_image per preview
        if self.instance and self.instance.pk and self.instance.image:
            self.fields['existing_image'].initial = self.instance.image.url

        self.fields['alt_text'].widget = forms.HiddenInput()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="text-primary">Immagine</h6>'),
                Field('existing_image'),
                Field('image'),
                Field('alt_text'),
                Field('is_main'),
                css_class='border rounded p-3 mb-3'
            )
        )


# inline formsets
CreateImageFormSet = inlineformset_factory(
    Product, ProductImage, form=ProductImageForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)
EditImageFormSet = inlineformset_factory(
    Product, ProductImage, form=ProductImageForm,
    extra=0, can_delete=True, min_num=0, validate_min=False
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description', 'image']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome categoria'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrizione (opzionale)'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crispy helper
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Field('description'),
                Field('image'),
                css_class='card-body'
            )
        )

    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit=False, *args, **kwargs)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


