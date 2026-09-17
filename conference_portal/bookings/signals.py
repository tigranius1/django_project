from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.base import ContentFile
from .models import BookingImage


@receiver(post_save, sender=BookingImage)
def create_thumbnail(sender, instance, created, **kwargs):
    if not created or not instance.image or instance.thumbnail:
        return
    try:
        img = PilImage.open(instance.image.path)
        img.thumbnail((300, 300))
        buffer = BytesIO()
        fmt = img.format or 'JPEG'
        img.save(buffer, format=fmt)
        filename = f'thumb_{instance.image.name.split("/")[-1]}'
        instance.thumbnail.save(filename, ContentFile(buffer.getvalue()), save=False)
        instance.save(update_fields=['thumbnail'])
    except Exception:
        pass