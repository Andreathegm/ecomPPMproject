from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from orders.models import Order
from products.models import Product, Category


@receiver(post_migrate)
def create_default_groups_and_permissions(sender, **kwargs):
    """
    Crea gruppi e permessi di default per l'e-commerce.

    SOLUZIONE AI PERMESSI "PROPRI" vs "ALTRUI":
    - Usiamo permessi Django standard + logica nelle view
    - Customer ha change_order ma nelle view controlliamo che sia il proprietario
    - Store Manager ha change_all_orders (permesso custom) per modificare tutto
    """

    # ---- Creiamo permessi personalizzati se non esistono ----
    order_content_type = ContentType.objects.get_for_model(Order)

    # Permesso custom per modificare TUTTI gli ordini
    change_all_orders_perm, created = Permission.objects.get_or_create(
        codename='change_all_orders',
        name='Can change all orders (including others)',
        content_type=order_content_type,
    )

    # Permesso custom per eliminare ordini
    delete_all_orders_perm, created = Permission.objects.get_or_create(
        codename='delete_all_orders',
        name='Can delete all orders (including others)',
        content_type=order_content_type,
    )

    # ---- Gruppo: Customer ----
    customer_group, _ = Group.objects.get_or_create(name='Customer')

    customer_permissions = []

    # Customer può gestire i PROPRI ordini
    order_permissions = Permission.objects.filter(
        content_type=order_content_type,
        codename__in=['add_order', 'view_order', 'change_order']
        # change_order sarà limitato ai propri nelle view
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

    # ---- Gruppo: Store Manager ----
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')

    # Store Manager: tutti i permessi del Customer + gestione completa
    manager_permissions = list(customer_permissions)

    # Aggiungi i permessi CUSTOM per gestire TUTTI gli ordini
    manager_permissions.extend([change_all_orders_perm, delete_all_orders_perm])

    # Gestione completa prodotti
    product_management = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Product),
        codename__in=['add_product', 'change_product', 'delete_product']
    )
    manager_permissions.extend(product_management)

    # Gestione completa categorie
    category_management = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Category),
        codename__in=['add_category', 'change_category', 'delete_category']
    )
    manager_permissions.extend(category_management)

    manager_group.permissions.set(manager_permissions)