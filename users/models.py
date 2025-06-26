from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        CUSTOMER = 'CU', _('Client')
        MANAGER = 'MA', _('Manager')

    user_type = models.CharField(
        max_length=2,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",  # Cambiato
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",  # Cambiato
        related_query_name="user",
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_manager(self):
        return self.user_type == self.UserType.MANAGER
