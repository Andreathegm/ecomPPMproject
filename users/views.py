# users/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class MyLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'auth/login.html'


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'auth/signup.html'
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response

# Create your views here.
