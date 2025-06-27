from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        CUSTOMER = 'CU', _('Cliente')
        MANAGER = 'MA', _('Store Manager')

    user_type = models.CharField(
        max_length=2,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
        verbose_name=_('Tipo utente')
    )

    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefono')
    address = models.TextField(blank=True, null=True, verbose_name='Indirizzo')

    REQUIRED_FIELDS = ['email']  # Richiesto oltre a username per creare superuser

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def is_manager(self):
        return self.user_type == self.UserType.MANAGER

    @property
    def is_customer(self):
        return self.user_type == self.UserType.CUSTOMER
