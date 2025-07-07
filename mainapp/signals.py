# signals.py

import logging
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy


@receiver(pre_save)
def cleanup_old_cloudinary_image(sender, instance, **kwargs):
    """
    Prima di salvare un oggetto:
    - se l’immagine è stata cambiata o rimossa, cancella la vecchia da Cloudinary.
    """
    # 1) Se il modello non usa CloudinaryField, esco subito
    if not hasattr(instance, '_meta'):
        return

    # 2) Se l’istanza non esiste ancora in DB (nuovo obj), non c’è immagine vecchia da cancellare
    if instance._state.adding:
        return

    # 3) Prendo l’istanza attuale dal DB per confrontare i campi
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return  # per sicurezza

    # 4) Scorro tutti i campi cercando i CloudinaryField
    for field in instance._meta.fields:
        if not isinstance(field, CloudinaryField):
            continue

        new_file = getattr(instance, field.name)
        old_file = getattr(old, field.name)

        # 5) Se c’era un’immagine precedente...
        if old_file:
            old_id = getattr(old_file, 'public_id', None)
            new_id = getattr(new_file, 'public_id', None)

            # 6) ...e l’hai sostituita o rimossa (diverso o None)...
            if old_id and old_id != new_id:
                print(f"[pre_save] Cancello vecchia immagine: {old_id}")
                try:
                    destroy(old_id)
                    print(f"[pre_save] Vecchia immagine '{old_id}' rimossa.")
                except Exception as e:
                    print(f"[pre_save] Errore eliminando '{old_id}': {e}")


@receiver(post_delete)
def delete_cloudinary_images(sender, instance, **kwargs):
    """
    Dopo aver cancellato un oggetto:
    - elimina l’immagine su Cloudinary se rimasta.
    """
    print(f"[post_delete] sender={sender.__name__}, instance={instance!r}")

    if not hasattr(instance, '_meta'):
        return

    for field in instance._meta.fields:
        print(f"[post_delete] Esamino campo '{field.name}'")
        if not isinstance(field, CloudinaryField):
            continue

        image_field = getattr(instance, field.name)
        if image_field:
            public_id = getattr(image_field, 'public_id', None)
            if public_id:
                print(f"[post_delete] Cancello immagine: {public_id}")
                try:
                    destroy(public_id)
                    print(f"[post_delete] Immagine '{public_id}' rimossa.")
                except Exception as e:
                    print(f"[post_delete] Errore eliminando '{public_id}': {e}")
