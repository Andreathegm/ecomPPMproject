from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Row, Column, Submit, HTML
from crispy_forms.bootstrap import FormActions
from .models import Product, ProductImage, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'stock', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Div(
                Row(
                    Column('category', css_class='form-group col-md-6 mb-3'),
                    Column('available', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('slug', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'

                ),
                Row(
                    Column('description', css_class='form-group col-md-12 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('price', css_class='form-group col-md-6 mb-3'),
                    Column('stock', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                css_class='card-body'
            )
        )

        # Personalizzazione dei campi
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Seleziona una categoria"
        self.fields['name'].widget.attrs.update({'placeholder': 'nome del prodotto'})
        self.fields['slug'].widget.attrs.update({'placeholder': 'slug del prodotto'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Descrizione del prodotto'})
        self.fields['price'].widget.attrs.update({'placeholder': '0.00'})
        self.fields['stock'].widget.attrs.update({'placeholder': 'Quantità disponibile'})


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_main']
        widgets = {
            'alt_text': forms.TextInput(attrs={'placeholder': 'Testo alternativo per l\'immagine'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Layout usando crispy forms
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<h6 class="mb-0">Immagine {{ forloop.counter }}</h6>'),
                    HTML('''
                        {% if not forloop.first %}
                            <button type="button" class="btn btn-outline-danger btn-sm remove-form">
                                <i class="fas fa-trash"></i> Rimuovi
                            </button>
                        {% endif %}
                    '''),
                    css_class='d-flex justify-content-between align-items-center mb-2'
                ),
                Row(
                    Column('image', css_class='form-group col-md-6 mb-3'),
                    Column('alt_text', css_class='form-group col-md-4 mb-3'),
                    css_class='row'
                ),
                Row(
                    Column('is_main', css_class='form-group mb-3')

                ),
                css_class='image-form-item border rounded p-3 mb-3'
            )
        )

        # Personalizzazione dei campi
        self.fields['image'].widget.attrs.update({
            'accept': 'image/*',
            'class': 'form-control'
        })
        self.fields['alt_text'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['is_main'].widget.attrs.update({
            'class': 'form-check-input'
        })

        # Personalizzazione delle label
        self.fields['image'].label = 'Immagine'
        self.fields['is_main'].label = 'Immagine principale'
        self.fields['alt_text'].label = 'Testo alternativo'


# Creazione del formset per le immagini
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    fields=['image', 'alt_text', 'is_main'],
    extra=2,  # Numero di form vuoti da mostrare inizialmente
    can_delete=True,
    can_delete_extra=True,
    min_num=1,  # Minimo una immagine richiesta
    validate_min=True,
    max_num=10,  # Massimo 10 immagini
    validate_max=True,
)


class ProductImageFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">Immagini del Prodotto</h5>'),
                HTML('<p class="text-muted small mb-3">Aggiungi almeno un\'immagine per il prodotto. Seleziona "Immagine principale" per l\'immagine che apparirà come copertina.</p>'),
                Div(
                    css_class='formset-container'
                ),
                HTML('''
                    <div class="mt-3">
                        <button type="button" class="btn btn-outline-secondary btn-sm" id="add-image-form">
                            <i class="fas fa-plus"></i> Aggiungi altra immagine
                        </button>
                    </div>
                '''),
                css_class='card-body'
            )
        )