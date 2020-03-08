from django.db import models
import random
# Create your models here.
from django.conf import settings
from django.utils import timesince, timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
def get_rand():
    return '{0:06}'.format(random.randint(000000, 1000000))

class Domain(models.Model):
    domain = models.CharField(max_length=30)

class Otp(models.Model):
    user = models.OneToOneField('zapuser.ZapUser', related_name='otp')
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    otp = models.IntegerField(default=get_rand)

class AppLinkSms(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    phone = models.CharField(max_length=20)
    def __unicode__(self):
        return unicode(self.phone+' -- '+timesince.timesince(self.created) + " ago.")

class CallRequest(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    def __unicode__(self):
        return unicode(self.phone+' '+self.email+' -- '+timesince.timesince(self.created) + " ago.")
        
@receiver(post_save, sender=CallRequest)
def callrequest_notification(sender, instance, created, **kwargs):
    if created:
        from zap_apps.zap_notification.views import ZapEmail
        zapemail = ZapEmail()
        zapemail.send_email_attachment("Luxury Closet Cleanup Lead", "info@zapyle.com", ["rashi@zapyle.com","freda@zapyle.com"],"There's a new signup for LCC on website. The phone number is - {}".format(instance.phone))

class Testimonial(models.Model):
    text = models.CharField(max_length=1000)
    user = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    def __unicode__(self):
        return unicode(self.text+' - '+self.user)