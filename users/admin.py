from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_user_type_display', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Dati aggiuntivi', {'fields': ('user_type', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'phone', 'address')}),
    )
