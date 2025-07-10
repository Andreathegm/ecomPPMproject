# users/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm


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

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'user/profile.html', {'form': form})
    else:
        form = ProfileForm(instance=user)

    return render(request, 'user/profile.html', {'form': form})
