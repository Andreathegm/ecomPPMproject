# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your password'
        })


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'username': 'pick a unique username',
            'email': 'insert your email address',
            'password1': 'pick a password',
            'password2': 'confirm your password',
        }

        for field_name, field in self.fields.items():
            # Aggiungi la classe Bootstrap a tutti i campi
            field.widget.attrs['class'] = 'form-control'

            # Aggiungi il placeholder se è stato definito
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address already exists.")
        return email
