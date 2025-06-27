from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from orders.models import Order
from products.models import Product, Category


@receiver(post_migrate)
def create_default_groups_and_permissions(sender, **kwargs):
    # ---- Gruppo: Customer ----
    customer_group, _ = Group.objects.get_or_create(name='Customer')
    customer_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Order),
        codename__in=['add_order', 'view_order', 'change_order']
    )
    customer_group.permissions.set(customer_permissions)

    # ---- Gruppo: Store Manager ----
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')

    manager_permissions = list(Permission.objects.filter(
        content_type__in=[
            ContentType.objects.get_for_model(Product),
            ContentType.objects.get_for_model(Category),
            ContentType.objects.get_for_model(Order)
        ],
        codename__in=[
            'add_product', 'change_product', 'delete_product', 'view_product',
            'add_category', 'change_category', 'delete_category', 'view_category',
            'view_order', 'change_order'  # Store manager può vedere e aggiornare gli ordini
        ]
    ))

    manager_group.permissions.set(manager_permissions)
