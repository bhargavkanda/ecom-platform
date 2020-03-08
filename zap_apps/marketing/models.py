from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from zap_apps.discover.models import ANDROID_ACTIVITY
from django.utils import timezone
from StringIO import StringIO
import requests
from PIL import Image
# Create your models here.
import pdb
from django.conf import settings
from celery.task.control import revoke
from django.core.exceptions import ValidationError
import datetime

ACTION_TYPES = (
    ('profile','profile'),
    ('product','product'),
    ('newsfeed','newsfeed'),
    ('filtered','filtered feed'),
    ('upload','upload'),
    ('own_profile','own_profile'),
    ('earn_cash', 'Earn Cash'),
    ('update_app', 'Update App'),
    ('deep_link', 'Deep Link'),
)

CONDITION_TYPES = (
    ('0','nurture_users'),
    ('1','location'),
    ('2','age'),
    ('3','sex'),
    ('4','birthday'),
)

NOTIFICATION_TYPE = (
    ('marketing','marketing'),
    ('transactional','transactional'),
)


class ClosetCleanup(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)


class Action(models.Model):
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, blank=True, null=True)
    data = JSONField(null=True, blank=True, default=dict())

    def get_args_string(self):
        # pdb.set_trace()
        result = ''
        for k,v in self.data.items():
            if 'price' in k:
                result += '&' + k + '='
                result += ",".join([str(i[0])+'-'+str(i[1]) for i in v])
            else:
                result+= '&' + k + '='
                result += ",".join([str(i) for i in v])
        return result[1:]


class Condition(models.Model):
    condition_type = models.CharField(max_length=4,choices=CONDITION_TYPES)
    value = ArrayField(JSONField(null=True, blank=True, default=dict()), default=list())


class Notifs(models.Model):
    text = models.CharField(max_length=1000)
    tag = ArrayField(models.CharField(max_length=50,null=True,blank=True), default=list())
    scheduled_time = models.DateTimeField(null=True,blank=True)
    action = models.ForeignKey('marketing.Action', null=True, blank=True, related_name='notif')
    condition = models.ManyToManyField('marketing.Condition', blank=True)
    # image = models.CharField(null=True,blank=True, max_length=1500)
    image = models.ImageField(upload_to="uploads/marketing/" ,blank=True, null=True)


class NotificationTracker(models.Model):
    user = models.ForeignKey('zapuser.ZapUser', related_name='user_notification')
    notif = models.ForeignKey('Notifs', related_name='notif_tracker')
    notif_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE)
    sent_time = models.DateTimeField()
    opened_time = models.DateTimeField(null=True,blank=True)


class UserMarketing(models.Model):
    user = models.OneToOneField('zapuser.ZapUser', related_name='marketing_user')
    nurture = models.IntegerField(default=0)
    test_campaign = models.BooleanField(default=False)
    mothers_day = models.BooleanField(default=False)
    big_bag_sale = models.BooleanField(default=False)
    speed_sale = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.zap_username or self.user.email


class ActionDefault(models.Model):
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, blank=True, null=True)
    ios_target = models.CharField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.ios_target)

class Overlay(models.Model):
    PLATFORM = (
        ('APP', 'app only'),
        ('WEBSITE', 'website only'),
        ('BOTH', 'both app and website'))
    PAGE = (
        ('feed', 'Feed'),
        ('product', 'Product'),
        ('profile', 'Profile'),
        ('my_profile', 'My Profile'),
        ('upload', 'Upload'),
        ('my_order', 'My Order'),
        ('my_info', 'My Info'))
    image = models.ImageField(upload_to='uploads/images/')
    image_width = models.IntegerField(default=500, null=True, blank=True)
    image_height = models.IntegerField(default=500, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    cta_text = models.CharField(max_length=30)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=False)
    platform = models.CharField(choices=PLATFORM, max_length=10)
    can_close = models.BooleanField(default=False)
    delay = models.IntegerField(default=0)
    page = models.CharField(choices=PAGE, default="feed", max_length=10)
    campaign = models.CharField(max_length=30)
    full_screen = models.BooleanField(default=False)
    uri_target = models.CharField(max_length=100, null=True, blank=True, help_text="http://dev.zapyle.com/catalogue/singleproduct/id/an/")
    activity_name = models.CharField(max_length=100, null=True, blank=True)
    action = models.ForeignKey('ActionDefault', null=True, blank=True)
    android_activity = models.CharField(choices=ANDROID_ACTIVITY, max_length=30, null=True, blank=True)
    show_limit = models.IntegerField(default=0)

    def in_time(self):
        return self.start_date <= timezone.now() <= self.end_date

    def __unicode__(self):
        return self.title
    def save(self, *args, **kwargs):
        if self.image:
            # with Image.open(settings.MEDIA_ROOT+self.image) as im:
            try:
                with Image.open(self.image) as im:
                    self.image_width, self.image_height = im.size
                    super(Overlay, self).save(*args, **kwargs)
            except:
                r_img = requests.get(self.image)
                im = Image.open(StringIO(r_img.content))
                self.image_width, self.image_height = im.size
                super(Overlay, self).save(*args, **kwargs)
        else:
            super(Overlay, self).save(*args, **kwargs)


class OverlaySeen(models.Model):
    overlay = models.ForeignKey('Overlay', related_name='overlay')
    user = models.ForeignKey('zapuser.ZapUser', related_name='overlay_seen_user')
    number_of_times_seen = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.overlay.title+" "+self.user.zap_username


"""
  Campaign Models - including Flash Sales
"""

class Campaign(models.Model):
    name = models.CharField(max_length=1000)
    slug = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    show_timer = models.BooleanField(default=True)
    offer = models.OneToOneField('offer.ZapOffer', related_name='campaign', blank=True, null=True)
    following_users = models.ManyToManyField('zapuser.ZapUser', related_name="following_campaigns", blank=True)
    following_leads = models.ManyToManyField('marketing.Lead', related_name="following_campaigns", blank=True)

    def __unicode__(self):
        return self.name

    def is_running(self):
        if self.offer.start_time < timezone.now() and self.offer.end_time > timezone.now():
            return True
        else:
            return False

    def in_future(self):
        if self.offer.start_time > timezone.now():
            return True
        else:
            return False


class CampaignProducts(models.Model):
    campaign = models.ForeignKey('Campaign', related_name="campaign_product")
    products = models.ForeignKey('zap_catalogue.ApprovedProduct', related_name="products")
    discount = models.FloatField()

    def __unicode__(self):
        return self.campaign.name

    class Meta:
        unique_together = ('campaign', 'products',)

class Lead(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    unique_code = models.CharField(max_length=200, editable=False, null=True, blank=True)
    referral_user = models.ForeignKey('zapuser.ZapUser', blank=True, null=True)
    referral_lead = models.ForeignKey('marketing.Lead', blank=True, null=True)
    acquired_campaign = models.ForeignKey('marketing.Campaign', blank=True)
    time = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    source = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.name + self.email + str(self.phone_number)

class Message(models.Model):
    note = models.TextField()
    email_phone = models.CharField(max_length=50)

from zap_apps.offer.tasks import send_email_to_zapyle
from django.dispatch import receiver
from django.db.models.signals import post_save
@receiver(post_save, sender=Message)
def message_notification(sender, instance, created, **kwargs):
    if created:
        if settings.CELERY_USE:
            send_email_to_zapyle(instance.note, instance.email_phone)
        else:
            send_email_to_zapyle(instance.note, instance.email_phone)

