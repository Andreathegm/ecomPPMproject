from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'shipping_name',
            'shipping_email',
            'shipping_phone',
            'shipping_address',
            'shipping_city',
            'shipping_postal_code',
            'shipping_country',
            'payment_method',
        ]
        widgets = {
            'shipping_name':        forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_email':       forms.EmailInput(attrs={'class': 'form-control'}),
            'shipping_phone':       forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address':     forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'shipping_city':        forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_country':     forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    ('credit_card', 'Credit card'),
                    ('paypal', 'PayPal'),
                    ('bank_transfer', 'Bank transfer'),
                ]
            ),
        }
