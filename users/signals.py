from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from orders.models import Order
from products.models import Product, Category


@receiver(post_migrate)
def create_default_groups_and_permissions(sender, **kwargs):


    order_content_type = ContentType.objects.get_for_model(Order)

    change_all_orders_perm, created = Permission.objects.get_or_create(
        codename='change_all_orders',
        name='Can change all orders (including others)',
        content_type=order_content_type,
    )

    delete_all_orders_perm, created = Permission.objects.get_or_create(
        codename='delete_all_orders',
        name='Can delete all orders (including others)',
        content_type=order_content_type,
    )

    customer_group, _ = Group.objects.get_or_create(name='Customer')

    customer_permissions = []

    order_permissions = Permission.objects.filter(
        content_type=order_content_type,
        codename__in=['add_order', 'view_order', 'change_order']
    )
    customer_permissions.extend(order_permissions)

    # Permessi per navigare il catalogo
    product_view = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Product),
        codename='view_product'
    )
    customer_permissions.extend(product_view)

    category_view = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Category),
        codename='view_category'
    )
    customer_permissions.extend(category_view)

    customer_group.permissions.set(customer_permissions)

    manager_group, _ = Group.objects.get_or_create(name='Store Manager')

    manager_permissions = list(customer_permissions)

    manager_permissions.extend([change_all_orders_perm, delete_all_orders_perm])

    product_management = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Product),
        codename__in=['add_product', 'change_product', 'delete_product']
    )
    manager_permissions.extend(product_management)

    category_management = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Category),
        codename__in=['add_category', 'change_category', 'delete_category']
    )
    manager_permissions.extend(category_management)

    manager_group.permissions.set(manager_permissions)