from django.db import models
# from zap_apps.'zapuser.ZapUser'.models import BrandTag
# from zap_apps.address.models import Address
from zap_apps.zap_catalogue.thumbs import ImageWithThumbsField
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from zap_apps.zap_notification.views import ZapEmail, PushNotification, ZapSms
from zap_apps.zap_notification.models import Notification
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from zap_apps.zap_catalogue.tasks import send_to_tornado, after_comment_post, after_love_notif, send_to_elasticsearch
from datetime import timedelta
from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField
from zap_apps.extra_modules.appvirality import AppViralityApi
from zap_apps.zapuser.models import AppViralityKey
from zap_apps.offer.tasks import apply_offers_task
from zap_apps.extra_modules.tasks import app_virality_conversion
from django.db.models import Q
from zap_apps.offer.models import ZapOffer
import requests

email = ZapEmail()
pushnots = PushNotification()
# Create your models here.
CATEGORY_TYPE = (
    ('FW', 'Foot Wears'),
    ('C', 'Clothes'),
    ('FS', 'Free Sizes'))
SALE_CHOICES = (
    ('1', 'SOCIAL'),
    ('2', 'SALE'),
)
AGE = (
    ('0', '0-3 months'),
    ('1', '3-6 months'),
    ('2', '6-12 months'),
    ('3', '1-2 years'),
)
CONDITIONS = (
    ('0', 'New with tags'),
    ('1', 'Mint Condition'),
    ('2', 'Gently loved'),
    ('3', 'Worn out'),
)
STATUS = (
    ('0', 'to be approved'),
    ('1', 'approved'),
    ('2', 'disapproved'),
    ('3', 'deleted'),
)
DISAPPROVED_REASONS = (
    ('0', 'The images are unclear'),
    ('1', 'The brand of product not shown in images'),
    ('2', 'The brand not accepted'),
    ('3', 'Incorrect information'),
    ('4', 'Other'),
)


class ProductViewTracker(DynamicDocument):
    user = StringField(max_length=30)
    products = ListField(DictField())


class Category(models.Model):
    """
    Category of Product. DB Table - zap_catalogue_category
    """
    name = models.CharField(max_length=50)
    category_type = models.CharField(
        choices=CATEGORY_TYPE, max_length=2, default="FW")
    description = models.TextField(max_length=10000, null=True, blank=True, help_text="This will be shown to the user")
    meta_description = models.TextField(max_length=10000, null=True, blank=True)
    web_cover = models.ImageField(
        upload_to="uploads/categorycover/", null=True, blank=True)
    mobile_cover = models.ImageField(
        upload_to="uploads/categorycover/", null=True, blank=True)
    slug = models.CharField(max_length=200, editable=False, unique=True, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)
    def set_slug(self):
        return self.name.lower().replace(" ", "-")
    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(Category, self).save(*args, **kwargs)


class SubCategory(models.Model):
    """
    Sub category of Product. DB Table - zap_catalogue_subcategory

    Related to  `zap_catalogue.Category` via  `parent`
    """
    name = models.CharField(max_length=50)
    name_singular = models.CharField(max_length=50, help_text="Enter the singular form of the name here. Eg: If Dresses is the sub category - enter Dress. This field is mandatory even if the original name is in singular form.")
    parent = models.ForeignKey('zap_catalogue.Category')
    category_type = models.CharField(
        choices=CATEGORY_TYPE, max_length=2, default="FW", null=True, blank=True)
    description = models.TextField(max_length=10000, null=True, blank=True, help_text="This will be shown to the user")
    meta_description = models.TextField(max_length=10000, null=True, blank=True)
    web_cover = models.ImageField(
        upload_to="uploads/subcategorycover/", null=True, blank=True)
    mobile_cover = models.ImageField(
        upload_to="uploads/subcategorycover/", null=True, blank=True)
    slug = models.CharField(max_length=200, editable=False, unique=True, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def set_slug(self):
        return self.name.lower().replace(" ", "-")

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(SubCategory, self).save(*args, **kwargs)

class ItemMeasurements(models.Model):
    length = models.FloatField()
    breadth = models.FloatField()
    height = models.FloatField()

    def __unicode__(self):
        return "Length - " + self.length + " Breadth - " + self.breadth + " Height - " + self.height

class BodyMeasurements(models.Model):
    bust = models.FloatField()
    natural_waist = models.FloatField()
    low_waist = models.FloatField()
    hips = models.FloatField()
    def __unicode__(self):
        return "Bust - " + self.bust + " Waist - " + self.natural_waist + " Hips - " + self.hips

class Size(models.Model):
    size = models.CharField(max_length=4)
    uk_size = models.CharField(max_length=4)
    us_size = models.CharField(max_length=4)
    eu_size = models.CharField(max_length=4)
    body_measurements = models.ForeignKey('zap_catalogue.BodyMeasurements', null=True, blank=True)
    category_type = models.CharField(choices=CATEGORY_TYPE, max_length=2)

    def __unicode__(self):
        return self.size + " uk-" + self.uk_size


class Brand(models.Model):
    brand = models.CharField(max_length=40)
    designer_brand = models.BooleanField(default=False)
    # logo = models.ImageField(
    #     upload_to="uploads/brandslogo/", null=True, blank=True)
    clearbit_logo = models.CharField(max_length=200, help_text="Go to (https://clearbit.com/logo), search for the brand name and get the link for the image. If it's no available on clearbit, get a square image from Google with minimum size of 600x600. First time? talk to RAMKY")
    tags = models.ManyToManyField('zapuser.BrandTag', blank=True, related_name="fff")
    description_short = models.CharField(max_length=200, null=True, blank=True, help_text="This will be shown to the user")
    description = models.TextField(max_length=10000, null=True, blank=True, help_text="This will be shown to the user")
    meta_description = models.TextField(max_length=10000, null=True, blank=True)
    web_cover = models.ImageField(
        upload_to="uploads/brandscover/", null=True, blank=True)
    mobile_cover = models.ImageField(
        upload_to="uploads/brandscover/", null=True, blank=True)
    slug = models.CharField(max_length=200, unique=True, editable=False, null=True, blank=True)
    following_users = models.ManyToManyField('zapuser.ZapUser', related_name="following_brands", blank=True)
    following_leads = models.ManyToManyField('marketing.Lead', related_name="following_brands", blank=True)
    brand_account = models.OneToOneField('zapuser.ZapUser', blank=True, null=True,
                                      related_name='representing_brand',
                                      help_text="if this brand is selling directly on Zapyle, create a user for the brand here by clicking on '+', if already created user select them.")

    def __unicode__(self):
        return unicode(self.brand)

    def set_slug(self):
        slug = self.brand.lower().replace(" ", "-")
        if slug.find('&') > -1:
            slug = slug.replace('&', 'and')
        return slug

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(Brand, self).save(*args, **kwargs)


class Occasion(models.Model):
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def set_slug(self):
        return self.name.lower().replace(" ", "-")

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(Occasion, self).save(*args, **kwargs)


class Color(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=10, null=True, blank=True)
    slug = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def set_slug(self):
        return self.name.lower().replace(" ", "-")

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(Color, self).save(*args, **kwargs)

class Style(models.Model):
    style_type = models.CharField(max_length=20)
    slug = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.style_type

    def set_slug(self):
        return self.style_type.lower().replace(" ", "-")

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(Style, self).save(*args, **kwargs)

def get_upload_path(instance, filename):
    return "uploads/product_images/" + "".join(str(timezone.now().date()).split("-")) + "/" + filename


class ProductImage(models.Model):
    image = ImageWithThumbsField("Image", upload_to=get_upload_path,
                                 blank=True, null=True, sizes=((100, 100), (150, 200), (500, 500), (600, 800), (1000, 1000), (1200, 1600), ("oc", "oc")))
    #image = models.ImageField(upload_to="uploads/product_images/original/", blank=True, null=True)

    def __unicode__(self):
        return unicode(self.image)


class Hashtag(models.Model):
    tag = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.tag)


class Hashtag1111111(models.Model):
    tag = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.tag)


import datetime


class Product(models.Model):
    pickup_address = models.ForeignKey(
        'address.Address', null=True, blank=True, on_delete=models.SET_NULL)
    images = models.ManyToManyField('zap_catalogue.ProductImage', blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    style = models.ForeignKey(Style, null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    original_price = models.FloatField(null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(default=timezone.now)
    sale = models.CharField(max_length=1, default='1', choices=SALE_CHOICES)
    listing_price = models.FloatField(null=True, blank=True)
    occasion = models.ForeignKey('zap_catalogue.Occasion', on_delete=models.SET_NULL, null=True, blank=True)
    product_category = models.ForeignKey(
        'zap_catalogue.SubCategory', on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey('zap_catalogue.Color', null=True, blank=True, on_delete=models.SET_NULL)
    completed = models.BooleanField(default=False)
    age = models.CharField(max_length=1, choices=AGE, null=True, blank=True)
    condition = models.CharField(
        max_length=1, choices=CONDITIONS, null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    size_type = models.CharField(max_length=10, null=True, blank=True, default='US')
    percentage_commission = models.FloatField(default=15)
    best_price = models.BooleanField(default=True)
    time_to_make = models.CharField(null=True, blank=True, max_length=200)
    status = models.CharField(
        max_length=1, default='0', choices=STATUS, null=True, blank=True)

    # shipping_charge = models.FloatField(null=True,blank=True,default=0)

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     self.discount = self.discount
    #     super(ModelClass, self).save(*args, **kwargs)
    def __unicode__(self):
        return unicode(self.id) + '  ' + unicode(self.title) + '. Seller - ' + unicode(self.user)

        # Overriding


class CustomManager(models.Manager):
    def get_queryset(self):
        return super(CustomManager, self).get_queryset().select_related('user')


# class AllManager(models.Manager):
#     def get_queryset(self):
#         return super(AllManager, self).get_queryset().select_related('user')
class APManager(models.Manager):
    def get_queryset(self):
        return super(APManager, self).get_queryset().select_related('user').filter(status='1')


class PTAManager(models.Manager):
    def get_queryset(self):
        return super(PTAManager, self).get_queryset().select_related('user').filter(status='0')


class DPManager(models.Manager):
    def get_queryset(self):
        return super(DPManager, self).get_queryset().select_related('user').filter(status='2')


class ApprovedProduct(Product):
    user = models.ForeignKey(
        'zapuser.ZapUser', related_name='approved_product')
    tags = models.ManyToManyField(
        'zap_catalogue.Hashtag', blank=True)
    extra_discount = models.FloatField(null=True, blank=True)
    product_tag = models.CharField(max_length=30, blank=True, null=True)
    loves = models.ManyToManyField(
        'zapuser.ZapUser', through='zap_catalogue.Loves', related_name='loved_products')
    seller_recommendations = models.ManyToManyField(
        'self', symmetrical=False, related_name='recommended_products', blank=True)
    disapproved_reason = models.CharField(
        max_length=1, choices=DISAPPROVED_REASONS, null=True, blank=True)
    with_zapyle = models.BooleanField(default=False)
    size = models.ManyToManyField(
        'zap_catalogue.Size', through='zap_catalogue.NumberOfProducts', through_fields=('product', 'size'), blank=True)
    score = models.IntegerField(default=100000)
    elastic_index = models.CharField(null=True, blank=True, max_length=200)
    partner_id = models.CharField(null=True, blank=True, max_length=200)
    cod_eligible = models.BooleanField(default=True)
    cashback = models.ForeignKey('offer.OfferBenefit', blank=True, null=True)
    objects = CustomManager()
    # all_objects = AllManager()
    ap_objects = APManager()
    pta_objects = PTAManager()
    dp_objects = DPManager()

    @property
    def shop(self):
        try: 
            if self.user.representing_brand and self.user.user_type.name == 'designer':
                if self.brand.id == 132:
                    shop_name = 7       # It's High Street
                else:
                    shop_name = 4       # It's International
                if self.user.representing_brand.designer_brand:
                    shop_name = 1     # It's Indian
        except:
            if self.user.user_type.name == 'zap_exclusive':
                shop_name = 2
            elif self.user.user_type.name in ['zap_user', 'zap_dummy', 'store_front']:
                shop_name = 3
        try:
            return shop_name
        except:
            return None
    class Meta:
        ordering = ['-score']

    def get_flash_sale_data(self):
        from zap_apps.marketing.models import CampaignProducts
        campaign_products = CampaignProducts.objects.filter(products=self.id, campaign__offer__start_time__lt=timezone.now(), campaign__offer__end_time__gt=timezone.now(), campaign__offer__status=True)
        if campaign_products:
            campaign_product = campaign_products[0]
            return {'extra_discount': str(int(campaign_product.discount)) + '% Off'}
        else:
            return None

    def get_offers(self, type=None, when=None, user_id=None):
        offers_data = []
        filter = Q()
        if type:
            filter &= Q(offer_type__in=list(type))
        if when:
            filter &= Q(offer_when__in=list(when))
        if not user_id:
            filter &= Q(offer_type__in=['SITE'])
        else:
            from zap_apps.zapuser.models import ZapUser
            user = ZapUser.objects.get(id=user_id)
            offers_ids = user.get_offers()
            filter &= Q(id__in=offers_ids)
        offers = ZapOffer.valid_objects.filter(filter).exclude(offer_type='HIDDEN')
        if offers:
            for offer in offers:
                if offer.offer_available_on_product(self.id):
                    offer_price = self.get_offer_price(offer.id)
                    offer_data = {'id': offer.id,'name': offer.name, 'description': offer.description, 'code': offer.code, 'offer_price': offer_price,
                                  'benefit': 'You save Rs. ' + str(int(self.listing_price - offer_price)), 'offer_benefit': int(self.listing_price - offer_price)}
                    if offer.show_timer:
                        offer_data.update({'valid_till': offer.validity(user_id) if user_id else offer.validity()})
                    offers_data.append(offer_data)
            if len(offers_data) > 0:
                return offers_data
            else:
                return None
        else:
            return None

    def get_offer_price(self, offer_code=None):
        from zap_apps.marketing.models import CampaignProducts
        if not offer_code:
            # offers_available = self.get_offers(type='SITE', when='ADD_CART')
            # if offers_available:
            #     product_data.update({'offer': {}})
            #     offer = offers_available[0]
            #     offer_code = offer.id
            # else:
            return self.listing_price
        try:
            if unicode(offer_code).isdigit():
                offer = ZapOffer.valid_objects.get(id=offer_code)
            else:
                offer = ZapOffer.valid_objects.get(code=offer_code)
            return (self.listing_price - offer.get_benefit(self.id))
            # return offer_price
        except Exception:
            return self.listing_price


    def get_title(self):
        return ((self.color.name + ' ') if self.color else (
            self.style.style_type + ' ') if self.style else '') + self.product_category.name_singular if self.user.user_type.name not in ['designer', 'zap_exclusive'] else self.title

    def save(self, *args, **kwargs):
        if self.sale == '2':
            if (self.original_price and self.listing_price):
                self.discount = (float(self.original_price) - float(
                    self.listing_price)) / float(self.original_price)
        super(ApprovedProduct, self).save(*args, **kwargs)


@receiver(post_save, sender=ApprovedProduct)
def approved_notification(sender, instance, created, **kwargs):
    print instance.status,'sssssstttttttaaaaaasssssss'
    cache.clear()
    if created:
        if settings.CELERY_USE:
            send_to_elasticsearch.delay(instance)            
            apply_offers_task.delay(when="LISTING", product=instance.id, user=instance.user.id)
        else:
            send_to_elasticsearch(instance)
            apply_offers_task(when="LISTING", product=instance.id, user=instance.user.id)

        # Add to Elastic Search Index
        # if settings.ELASTIC_INDEX:
        #     from zap_apps.zap_catalogue.elastic_search import ElasticSearch
        #     e = ElasticSearch()
        #     e.add_index(e, instance.id)
    else:
        if settings.CELERY_USE:
            send_to_elasticsearch.delay(instance)
        else:
            send_to_elasticsearch(instance)
        # Update Existing Elastic Search index
        # if settings.ELASTIC_INDEX:
        #     from zap_apps.zap_catalogue.elastic_search import ElasticSearch
        #     e = ElasticSearch()
        #     e.update_index(e, instance.id)


@receiver(pre_delete, sender=ApprovedProduct)
def remove_elastic_index(sender, instance, using, **kwargs):
    response = requests.delete(settings.ELASTIC_URL+str(instance.id))


class NumberOfProducts(models.Model):
    product = models.ForeignKey(
        'zap_catalogue.ApprovedProduct', blank=True, null=True, related_name='product_count')
    size = models.ForeignKey('zap_catalogue.Size', blank=True, null=True, related_name='sized_products')
    measurements = models.ForeignKey('zap_catalogue.ItemMeasurements', null=True, blank=True)
    quantity = models.IntegerField(default=1)
    time_to_make = models.CharField(max_length=200, null=True, blank=True)
    alternate_size = models.ForeignKey(
        'zap_catalogue.Size', null=True, blank=True, related_name='alternate_sized_products')

    def __unicode__(self):
        return unicode(self.product) + " " + unicode(self.size)

    class Meta:
        unique_together = ('product', 'size',)

@receiver(post_save, sender=NumberOfProducts)
def update_elastic(sender, instance, created, **kwargs):
    current_score = instance.product.score
    quantity_available = sum(instance.product.product_count.values_list('quantity',flat=True))
    ###### making product to top ############
    if quantity_available and current_score <= 0:
        days = (timezone.now() - instance.product.upload_time).days
        instance.product.score = 100000 - days
        instance.product.save()
    ###### making product to bottom #########
    elif not quantity_available and current_score > 0:
        instance.product.score = 0
        instance.product.save()
    else:
        if settings.CELERY_USE:
            send_to_elasticsearch.delay(instance.product)
        else:
            send_to_elasticsearch(instance.product)

class Loves(models.Model):
    product = models.ForeignKey(
        'zap_catalogue.ApprovedProduct', null=True, blank=True, related_name='likes_got')
    # like_count = models.IntegerField(null=True)
    loved_by = models.ForeignKey('zapuser.ZapUser', null=True, blank=True)
    loved_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.product)


# @receiver(post_save, sender=Loves)
# def love_notification(sender, instance, created, **kwargs):
#     if created:
#         if settings.CELERY_USE:
#             after_love_notif.apply_async(args=[instance.id], countdown=30)
#         else:
#             after_love_notif(instance.id)


class Comments(models.Model):
    product = models.ForeignKey(
        'zap_catalogue.ApprovedProduct', related_name='comments_got')
    # comment_count = models.IntegerField(null=True)
    commented_by = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, related_name='commenter')
    comment = models.CharField(max_length=1000)
    comment_time = models.DateTimeField(auto_now_add=True, editable=False)

    # mentioned_users
    # comment_time = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
        # ret = self.comment
        return self.comment

    class Meta:
        ordering = ['-comment_time']


class Conversations(models.Model):
    comment = models.ForeignKey('zap_catalogue.Comments', related_name='comment_mentions')
    mentions = models.ManyToManyField('zapuser.ZapUser')

    def __unicode__(self):
        # ret = self.comment
        return unicode(self.comment.id)


# @receiver(post_save, sender=Comments)
def comment_notification(sender, instance, created, **kwargs):
    if created:
        if settings.CELERY_USE:
            after_comment_post.apply_async(args=[instance.id], countdown=60)
        else:
            after_comment_post(instance.id)

@receiver(post_save, sender=NumberOfProducts)
@receiver(post_save, sender=Loves)
@receiver(post_save, sender=Comments)
def cache_clear1(sender, instance, created, **kwargs):
    cache.clear()


@receiver(post_delete, sender=ApprovedProduct)
def cacheclear2(sender, instance, **kwargs):
    cache.clear()


class ZapCuratedEntryImages(models.Model):
    image = models.ImageField(upload_to="uploads/zapcuratedentryimages/")


class ZapCuratedEntry(models.Model):
    brand = models.ForeignKey(Brand)
    original_price = models.FloatField()
    upload_time = models.DateTimeField(auto_now_add=True)
    product_category = models.ForeignKey('zap_catalogue.SubCategory')
    age = models.CharField(max_length=1, choices=AGE)
    condition = models.CharField(max_length=1, choices=CONDITIONS)
    images = models.ManyToManyField(ZapCuratedEntryImages)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=255)
