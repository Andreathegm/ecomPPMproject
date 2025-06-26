from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # Campi che il cliente compila durante il checkout
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
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'payment_method': forms.Select(choices=[
                ('credit_card',   'Carta di credito'),
                ('paypal',        'PayPal'),
                ('bank_transfer', 'Bonifico bancario'),
            ]),
        }
        labels = {
            'shipping_name':         'Nome destinatario',
            'shipping_email':        'Email destinatario',
            'shipping_phone':        'Telefono',
            'shipping_address':      'Indirizzo di spedizione',
            'shipping_city':         'Città',
            'shipping_postal_code':  'CAP',
            'shipping_country':      'Nazione',
            'payment_method':        'Metodo di pagamento',
        }
