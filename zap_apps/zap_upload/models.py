from django.db import models
from django.conf import settings
# Create your models here.
from zap_apps.zap_catalogue.models import Product
from zap_apps.zap_catalogue.thumbs import ImageWithThumbsField
from django.db.models.signals import post_save
from django.dispatch import receiver
from zap_apps.zap_notification.views import PushNotification
from zap_apps.zap_notification.models import Notification
from django.core.cache import cache
from zap_apps.offer.tasks import apply_offers_task

pushnots = PushNotification()

class MyModel(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    upload = ImageWithThumbsField("Image", upload_to="uploads/product_images/original/",
                                  blank=True, null=True, sizes=((125, 125), (300, 300),))
