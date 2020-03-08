from django.db import models
from PIL import Image
import pdb
from django.utils import timezone
from datetime import timedelta
import datetime

# from zap_apps.zap_catalogue.models import ApprovedProduct

# Create your models here.

ACTION_TYPES = (
    ('profile', 'profile'),
    ('product', 'product'),
    ('newsfeed', 'newsfeed'),
    ('filtered', 'filtered feed'),
    ('upload', 'upload'),
    ('own_profile', 'own_profile'),
    ('earn_cash', 'Earn Cash'),
    ('discover', 'Discover'),
    ('cart', 'Cart'),
    ('chat', 'Chat'),
    ('discover', 'Discover'),
    ('download_app', 'Download App'),

)

ANDROID_ACTIVITY = (
    ('FilteredFeed', 'Filtered Feed'),
    ('FeedPage', 'Newsfeed and filtered page'),
    ('ProfilePage', 'ProfilePage page'),
    ('Upload1', 'Upload page'),
    ('ProductPage', 'Product page'),
    ('MyProfile', 'Own profile page'),
    ('EarnCash', 'Earn Cash Page'),
)

import django

class Screens(models.Model):
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class Homefeed(models.Model):
    """Model for Homefeed. This is the super model which controls what needs to be shown in the Home page and in which order."""
    banner = models.ForeignKey('Banner', related_name='home_banner', null=True, blank=True)
    message = models.ForeignKey('Message', related_name='home_message', null=True, blank=True)
    product_collection = models.ForeignKey('ProductCollection', related_name='home_products', null=True, blank=True)
    user_collection = models.ForeignKey('UserCollection', related_name='home_users', null=True, blank=True)
    closet = models.ForeignKey('Closet', related_name='home_closet', null=True, blank=True)
    custom_collection = models.ForeignKey('CustomCollection', related_name='home_collection', null=True, blank=True)
    generic = models.ForeignKey('Generic', related_name='home_generic', null=True, blank=True)
    importance = models.IntegerField(default=1, unique=True)
    active = models.BooleanField(default=True)
    start_time = models.DateTimeField(default=django.utils.timezone.now)
    end_time = models.DateTimeField(default=django.utils.timezone.now)
    show_in = models.ManyToManyField('Screens', related_name='collections_in_screen', blank=True)
    PLATFORMS = (
        ('0', 'website & app'),
        ('1', 'app only'),
        ('2', 'website only')
    )
    platform = models.CharField(choices=PLATFORMS, max_length=2, default=0)
    def __unicode__(self):
        return unicode(self.banner or self.message or self.closet or self.generic or self.product_collection or self.custom_collection or self.user_collection)

    def save(self, *args, **kwargs):
        if self.start_time == self.end_time:
            self.end_time = timezone.now() + timedelta(days=365)
        super(Homefeed, self).save(*args, **kwargs)

# class WebsiteHomefeed(models.Model):
#     """Model for Homefeed. This is the super model which controls what needs to be shown in the Home page and in which order."""
#     title = models.CharField(max_length=30, null=True, blank=True)
#     banner = models.ForeignKey('Banner', related_name='website_home_banner', null=True, blank=True)
#     message = models.ForeignKey('Message', related_name='website_home_message', null=True, blank=True)
#     product_collection = models.ForeignKey('ProductCollection', related_name='website_home_products', null=True, blank=True)
#     user_collection = models.ForeignKey('UserCollection', related_name='website_home_users', null=True, blank=True)
#     closet = models.ForeignKey('Closet', related_name='website_home_closet', null=True, blank=True)
#     custom_collection = models.ForeignKey('CustomCollection', related_name='website_home_collection', null=True, blank=True)
#     generic = models.ForeignKey('Generic', related_name='website_home_generic', null=True, blank=True)
#     importance = models.IntegerField(default=1, unique=True)
#     active = models.BooleanField(default=True)
#     start_time = models.DateTimeField(default=timezone.now())
#     end_time = models.DateTimeField(default=timezone.now()+timedelta(days=365))
#     def __unicode__(self):
#         return unicode(self.title) +' -- '+ unicode(self.active) +' -- '+ unicode(self.importance)


class ZapAction(models.Model):
    android_activity = models.CharField(choices=ANDROID_ACTIVITY, max_length=30, null=True, blank=True)
    action_type = models.CharField(choices=ACTION_TYPES, max_length=20)
    collection_filter = models.CharField(max_length=1000, null=True, blank=True)
    new_target = models.CharField(max_length=1000, null=True, blank=True, editable=False)
    ios_target = models.CharField(max_length=1000, null=True, blank=True)
    target = models.CharField(max_length=1000, null=True, blank=True)
    android_target = models.CharField(max_length=1000, null=True, blank=True, default='/filters/getProducts/1/an/')
    website_target = models.CharField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id) + ' -- ' + self.action_type or '' + ' -- ' + self.collection_filter or ''


class Banner(models.Model):
    """Model for Banner. The first template that comes up in the homepage."""

    title = models.CharField(max_length=200, null=True, blank=True, help_text="This will be shown to the user")
    description = models.TextField(max_length=2000, null=True, blank=True, help_text="This will be shown to the user")
    meta_description = models.TextField(max_length=2000, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/homepage_images/banner/', null=True, blank=True)
    collection_image_mobile = models.ImageField(upload_to='uploads/homepage_images/banner/', null=True, blank=True)
    image_web = models.ImageField(upload_to='uploads/homepage_images/banner/', blank=True, null=True)
    collection_image_web = models.ImageField(upload_to='uploads/homepage_images/banner/', null=True, blank=True)
    action = models.ForeignKey('ZapAction', related_name='banner_action')
    seo_description = models.TextField(max_length=10000, null=True, blank=True)
    alt_tags = models.CharField(max_length=2000, null=True, blank=True)
    image_width = models.IntegerField(default=500, null=True, blank=True, editable=False)
    image_height = models.IntegerField(default=500, null=True, blank=True, editable=False)
    collection_image_width = models.IntegerField(default=500, null=True, blank=True, editable=False)
    collection_image_height = models.IntegerField(default=500, null=True, blank=True, editable=False)
    slug = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return (self.title or unicode(self.image)) + '  --  ' +self.slug
    def save(self, *args, **kwargs):
        if self.image or self.collection_image_mobile:
            if self.image:
                with Image.open(self.image) as im:
                    self.image_width, self.image_height = im.size
                    super(Banner, self).save(*args, **kwargs)
            if self.collection_image_mobile:
                with Image.open(self.collection_image_mobile) as im:
                    self.collection_image_width, self.collection_image_height = im.size
                    super(Banner, self).save(*args, **kwargs)
        else:
            super(Banner, self).save(*args, **kwargs)


class Message(models.Model):
    """Model for Message. A short description like template"""

    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    background_color = models.CharField(max_length=30, default='FBFBFB', null=True, blank=True)
    text_color = models.CharField(max_length=30, default='B7B7B7', null=True, blank=True)

    def __unicode__(self):
        return self.title or self.description


class ProductCollection(models.Model):
    """Model for ProductCollection. products will be showcased on the homepage based on this model.
	If number is null, show all products of product else randomize according to number.
	If product is null, show products based on onboarding data and number.
	"""
    title = models.CharField(max_length=50, null=True, blank=True)
    product = models.ManyToManyField('zap_catalogue.ApprovedProduct', blank=True, related_name='in_collection')
    description = models.CharField(max_length=500, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    header_image = models.ImageField(upload_to='uploads/homepage_images/banner/', blank=True, null=True)
    cta_text = models.CharField(max_length=50, default='View All')

    def __unicode__(self):
        return unicode(self.title) + unicode(self.product.values_list('title',flat=True))


class UserCollection(models.Model):
    user = models.ManyToManyField('zapuser.ZapUser', blank=True)
    number = models.IntegerField(null=True, blank=True)
    cta = models.ForeignKey('CTA', null=True, blank=True)

    def __unicode__(self):
        return unicode(self.user.values_list('zap_username', flat=True))


class Closet(models.Model):
    """Model for Closet. Each Closet will have 1 user and their multiple products"""
    title = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey('zapuser.ZapUser', related_name='closet_user')
    product = models.ManyToManyField('zap_catalogue.ApprovedProduct', blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    cta = models.ForeignKey('CTA', null=True, blank=True)
    image = models.ImageField(upload_to='uploads/homepage_images/closet/', null=True, blank=True)
    image_width = models.IntegerField(default=500, null=True, blank=True)
    image_height = models.IntegerField(default=500, null=True, blank=True)

    def __unicode__(self):
        return self.user.zap_username

    def save(self, *args, **kwargs):
        if self.image:
            with Image.open(self.image) as im:
                self.image_width, self.image_height = im.size
                super(Closet, self).save(*args, **kwargs)
        else:
            super(Closet, self).save(*args, **kwargs)

class CustomCollection(models.Model):
    """Model for Collection. This model is used to show filter types.
	"""
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    collection = models.ManyToManyField('Banner', blank=True)
    IN_ROW = (
        ('2', '2'),
        ('3', '3'),
        ('6', '6'),
    )
    number_in_row = models.CharField(choices=IN_ROW, max_length=2, default=2)

    def __unicode__(self):
        return unicode(self.title) + unicode(self.collection.values_list('title',flat=True))


class Generic(models.Model):
    """Model for Generic. It will contain data for all generic template. Eg. The invitation template"""
    title = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/homepage_images/generic/', null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    cta = models.ForeignKey('CTA', null=True, blank=True)
    action = models.ForeignKey('ZapAction', related_name='generic_action')
    image_width = models.IntegerField(default=500, null=True, blank=True)
    image_height = models.IntegerField(default=500, null=True, blank=True)

    def __unicode__(self):
        return self.title or self.description

    def save(self, *args, **kwargs):
        if self.image:
            with Image.open(self.image) as im:
                self.image_width, self.image_height = im.size
                super(Generic, self).save(*args, **kwargs)
        else:
            super(Generic, self).save(*args, **kwargs)            

class CTA(models.Model):
    text = models.CharField(max_length=30, null=True, blank=True)
    background_color = models.CharField(max_length=30, default='FF5578')
    text_color = models.CharField(max_length=30, default='FFEBEF')
# target = models.CharField(max_length=1000, null=True, blank=True)
