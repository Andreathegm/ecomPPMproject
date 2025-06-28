# cart/utils.py

from django.conf import settings
from .models import Cart


def get_or_create_cart(request):
    # Assicuriamoci di avere sempre session_key
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    print(session_key)
    user = request.user if request.user.is_authenticated else None
    print(user)

    # Se l'utente è autenticato
    if user:
        # 1) prendi o crea il carrello aperto legato all'utente
        cart, created = Cart.objects.get_or_create(
            user=user,
            status=Cart.Status.OPEN,
            defaults={'cart_id': session_key}
        )
        # 2) controlla se esisteva un carrello anonimo con questa session_key
        try:
            anon = Cart.objects.get(
                user__isnull=True,
                cart_id=session_key,
                status=Cart.Status.OPEN
            )
        except Cart.DoesNotExist:
            anon = None

        # 3) se esiste, sposta gli item e cancella il carrello anonimo
        if anon and anon.pk != cart.pk:
            for item in anon.items.all():
                # se il prodotto è già nel cart dell'utente, somma quantità
                ci, _ = cart.items.get_or_create(
                    product=item.product,
                    defaults={'quantity': item.quantity, 'unit_price': item.unit_price}
                )
                if not _:
                    ci.quantity += item.quantity
                    ci.save()
            anon.delete()

        return cart

    # Utente anonimo: carrello basato su session_key
    cart, _ = Cart.objects.get_or_create(
        user=None,
        cart_id=session_key,
        status=Cart.Status.OPEN
    )
    return cart


def get_existing_cart(request):
    skey = request.session.session_key
    if skey:
        try:
            return Cart.objects.get(cart_id=skey, status=Cart.Status.OPEN)
        except Cart.DoesNotExist:
            pass

    if request.user.is_authenticated:
        try:
            return Cart.objects.get(user_id=request.user.pk, status=Cart.Status.OPEN)
        except Cart.DoesNotExist:
            pass

    return None
