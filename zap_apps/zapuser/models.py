from django.db import models
from django.contrib.auth.models import User
from push_notifications.models import GCMDevice, GCMDeviceManager
from zap_apps.order import zap_wallet
from zap_apps.account.models import get_rand
from zap_apps.zap_catalogue.thumbs import ImageWithThumbsField
from django.conf import settings
from zap_apps.account.models import Domain
from django.core.cache import cache
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum, F
from zap_apps.offer.tasks import apply_offers_task
from django.contrib.auth.signals import user_logged_in
import pdb
from zap_apps.cart.models import Cart
# from zap_apps.zap_catalogue.models import Size, Brand
# Create your models here.


USER_TYPES = (
    ('designer', ['designer']),
    ('vintage', ['zap_exclusive']),
    ('marketplace', ['zap_user', 'zap_dummy', 'store_front']),
    ('brand', ['designer']),
    )


@receiver(user_logged_in)
def login_trigger(sender, user, request, **kwargs):
    if sender.__name__=="ZapUser":
        from zap_apps.extra_modules.tasks import mixpanel_task
        if settings.CELERY_USE:
            mixpanel_task.delay(user.id, "Logged In", "Login")
        else:
            mixpanel_task(user.id, "Logged In", "Login")


class ZAPGCMDevice(GCMDevice):
    objects = GCMDeviceManager()
    logged_device = models.ForeignKey(
        'zapuser.LoggedDevice', related_name="zapgcm_device")
    app_version = models.CharField(max_length=15, null=True, blank=True)
    def __unicode__(self):
        return unicode((self.user.zapuser.zap_username or '') +' '+ (self.user.zapuser.email or '')+' '+ (self.registration_id or ''))


class WaistSize(models.Model):
    size = models.CharField(max_length=2)

    def __unicode__(self):
        return unicode(self.size)


class BrandTag(models.Model):
    tag = models.CharField(max_length=100)
    order = models.IntegerField(default=1)
    related_tags = models.ManyToManyField('self')

    def __unicode__(self):
        return self.tag


class ZapRole(models.Model):
    name = models.CharField(max_length=15, default="zap_user")

    def __unicode__(self):
        return self.name


class LoggedFrom(models.Model):
    name = models.CharField(max_length=10, default="zapyle")

    def __unicode__(self):
        return self.name


class LoggedDevice(models.Model):
    name = models.CharField(max_length=10, default="website")

    def __unicode__(self):
        return self.name


def get_role():
    return ZapRole.objects.get(name="zap_user").id


def get_logged_from():
    return LoggedFrom.objects.get(name="zapyle").id


def get_logged_device():
    return LoggedDevice.objects.get(name="website").id


class ZapUser(User):
    zap_username = models.CharField(
        max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(null=True, blank=True, max_length=14)
    logged_from = models.ForeignKey(
        'zapuser.LoggedFrom', default=get_logged_from, null=True, on_delete=models.SET_NULL)
    logged_device = models.ForeignKey(
        'zapuser.LoggedDevice', default=get_logged_device, null=True, on_delete=models.SET_NULL)
    upload_access = models.BooleanField(default=False)
    user_type = models.ForeignKey('zapuser.ZapRole', default=get_role, null=True, on_delete=models.SET_NULL)
    pushBotToken = models.CharField(max_length=500, null=True, blank=True)
    fb_id = models.CharField(max_length=100, null=True, blank=True)
    instagram_id = models.CharField(max_length=100, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_number_verified = models.BooleanField(default=False)
    citrus_seller_id = models.CharField(max_length=30, null=True, blank=True)

    @property
    def cart(self):
        cart, c = Cart.objects.get_or_create(user=self)
        return cart

    def balance_wallet(self):
        zap = zap_wallet.ZapWallet2()
        result = zap.balance(self.email, self.phone_number)
        return result

    def redeem_zap_wallet(self, amount, transaction=None):
        # import pdb; pdb.set_trace()
        zap = zap_wallet.ZapWalletView()
        affiliate_balance = self.get_affiliate_balance()
        promo_balance = self.get_promo_balance()
        return_balance = self.get_return_balance()
        if amount > affiliate_balance:
            #redeem affiliate balance
            if affiliate_balance:
                zap.redeem(affiliate_balance, mode='0', user_id=self, purpose="Debited for transaction - "+ str(transaction.id), transaction=transaction)
            amount -= affiliate_balance
        else:
            zap.redeem(amount, mode='0', user_id=self, purpose="Debited for transaction - "+ str(transaction.id), transaction=transaction)
            return amount, 0, 0
            # amount -= affiliate_balance

        if amount > promo_balance:
            if promo_balance:
                zap.redeem(promo_balance, mode='1', user_id=self, purpose="Debited for transaction - "+ str(transaction.id), transaction=transaction)
            amount -= promo_balance
        else:
            zap.redeem(amount, mode='1', user_id=self, purpose="Debited for transaction - "+ str(transaction.id), transaction=transaction)
            return affiliate_balance, amount, 0

        zap.redeem(amount, mode='2', user_id=self, purpose="Debited for transaction - "+ str(transaction.id), transaction=transaction)
        return affiliate_balance, promo_balance, amount

    def unread_notif_count(self):
        return self.notification.filter(read=False).count()
    
    # def issue_return_wallet(self, amount, return_id=None):
    #     zap = zap_wallet.ZapWalletView()
    #     return zap.issue(
    #         amount, self.id, return_id=return_id)

    def create_zapsession(self):
        ZapSession.objects.create(user=self)

    def issue_zap_wallet(self, amount, mode='0' ,purpose=None, return_id=None, promo=None):
        # from zap_apps.payment.models import ZapWallet
        zap = zap_wallet.ZapWalletView()
        return zap.issue(amount=amount, mode=mode, user_id=self ,purpose=purpose, return_id=return_id, promo=promo)

    def get_affiliate_balance(self):
        from zap_apps.payment.models import ZapWallet
        return (ZapWallet.objects.filter(user=self, credit=True, mode='0').aggregate(s=Sum(F('amount')))['s'] or 0) - (ZapWallet.objects.filter(user=self, credit=False, mode='0').aggregate(s=Sum(F('amount')))['s'] or 0)

    def get_promo_balance(self):
        from zap_apps.payment.models import ZapWallet
        return (ZapWallet.objects.filter(user=self, credit=True, mode='1').aggregate(s=Sum(F('amount')))['s'] or 0) - (ZapWallet.objects.filter(user=self, credit=False, mode='1').aggregate(s=Sum(F('amount')))['s'] or 0)

    def get_return_balance(self):
        from zap_apps.payment.models import ZapWallet
        return (ZapWallet.objects.filter(user=self, credit=True, mode='2').aggregate(s=Sum(F('amount')))['s'] or 0) - (ZapWallet.objects.filter(user=self, credit=False, mode='2').aggregate(s=Sum(F('amount')))['s'] or 0)

    @property
    def get_zap_wallet(self):
        from zap_apps.payment.models import ZapWallet
        return (ZapWallet.objects.filter(user=self, credit=True).aggregate(s=Sum(F('amount')))['s'] or 0) - (ZapWallet.objects.filter(user=self, credit=False).aggregate(s=Sum(F('amount')))['s'] or 0)

    def get_approved_products(self):
        from zap_apps.zap_catalogue.models import ApprovedProduct
        products = ApprovedProduct.ap_objects.filter(user=self)
        return products

    def get_offers(self):
        from zap_apps.offer.models import ZapOffer
        offers_ids = []
        offers = ZapOffer.objects.filter(end_time__gt=timezone.now(), start_time__lt=timezone.now(), status=True)
        for offer in offers:
            if offer.offer_available_for_user(self.id):
                offers_ids.append(offer.id)
        if len(offers_ids) > 0:
            return offers_ids
        else:
            return []

    def __unicode__(self):
        return self.zap_username or self.email or self.username

    class Meta:
        ordering = ['-date_joined']


class Subscriber(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    monthly_spend = models.IntegerField(blank=True, null=True)
    brands = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return (self.name if self.name else '')


class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    zapyle_users = models.ManyToManyField('zapuser.ZapUser', blank=True, null=True)
    leads = models.ManyToManyField('marketing.Lead', blank=True, null=True)
    emails = models.CharField(max_length=9999, blank=True, null=True)
    phone_numbers = models.CharField(max_length=9999, blank=True, null=True)

    def __unicode__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=200,   null=True, blank=True)

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField('zapuser.ZapUser', related_name='profile')
    SEX = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    MARITAL = (
        ('S', 'Single'),
        ('M', 'Married'),
    )
    dob = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    disclaimer = models.TextField(max_length=1000, null=True, blank=True, help_text="This disclaimer will be shown on all the products of the seller")
    profile_pic = models.CharField(max_length=200,   null=True, blank=True)
    _profile_pic = models.CharField(max_length=200,   null=True, blank=True, db_column='profile_pic')
    cover_pic = models.ImageField(
        upload_to="uploads/covers/", null=True, blank=True)
    pro_pic = ImageWithThumbsField("Image", upload_to="uploads/profile_images/",
                                 blank=True, null=True, sizes=((100, 100), (500, 500)), default=None)
    verified = models.BooleanField(default=False)
    admiring = models.ManyToManyField(
        'zapuser.ZapUser', blank=True, related_name="aaaa")
    city = models.ForeignKey('zapuser.City', null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX, null=True, blank=True)
    marital_status = models.CharField(

        max_length=10, choices=MARITAL, null=True, blank=True)
    profile_completed = models.IntegerField(default=1)
    zap_score = models.FloatField(default=1)
    normalized_zap_score = models.FloatField(default=1)

    @property
    def profile_pic(self):
        return (((settings.CURRENT_DOMAIN if hasattr(settings, 'CURRENT_DOMAIN') else Domain.objects.first().domain if Domain.objects.first() else "") + self.pro_pic.url_100x100) if (hasattr(self, 'pro_pic') and self.pro_pic) else None) or self._profile_pic or ((settings.CURRENT_DOMAIN if hasattr(settings, 'CURRENT_DOMAIN') else Domain.objects.first().domain if Domain.objects.first() else "") + settings.STATIC_URL+settings.PLACEHOLDER_IMG_URL)

    @property
    def profile_pic_original(self):
        return (((settings.CURRENT_DOMAIN if hasattr(settings,'CURRENT_DOMAIN') else Domain.objects.first().domain if Domain.objects.first() else "") + self.pro_pic.url) if (hasattr(self, 'pro_pic') and self.pro_pic) else None) or self._profile_pic or ((settings.CURRENT_DOMAIN if hasattr(settings,'CURRENT_DOMAIN') else Domain.objects.first().domain if Domain.objects.first() else "") + settings.STATIC_URL + settings.PLACEHOLDER_IMG_URL)

    @profile_pic.setter
    def profile_pic(self, value):
        self._profile_pic = value

    def __unicode__(self):
        return self.user.email or self.user.zap_username or self.user.username


@receiver(m2m_changed, sender=UserProfile.admiring.through)
def cache_clear_admire(sender, instance, **kwargs):
    cache.clear()


class UserData(models.Model):
    user = models.OneToOneField('zapuser.ZapUser', related_name='user_data')
    account_number = models.CharField(max_length=100, null=True, blank=True)
    account_holder = models.CharField(max_length=30, null=True, blank=True)
    old_account_number = models.CharField(
        max_length=100, null=True, blank=True)
    credit_amt = models.FloatField(null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    old_ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    evangelist = models.ForeignKey('zapuser.EvangeList', null=True, blank=True)
    fb_friends_list = models.ManyToManyField('zapuser.ZapUser')

    def __unicode__(self):
        return self.user.email or self.user.zap_username or self.user.username


class UserPreference(models.Model):
    user = models.OneToOneField(
        'zapuser.ZapUser', related_name='fashion_detail')
    size = models.ManyToManyField(
        'zap_catalogue.Size', blank=True, related_name="cloth_size")
    brand_tags = models.ManyToManyField('zapuser.BrandTag', blank=True)
    brands = models.ManyToManyField('zap_catalogue.Brand', blank=True)
    waist_size = models.ManyToManyField(
        'zapuser.WaistSize', blank=True, related_name='User')
    foot_size = models.ManyToManyField(
        'zap_catalogue.Size', blank=True, related_name="foot_size")

    def __unicode__(self):
        return self.user.email or self.user.zap_username or self.user.username


class ZapExclusiveUserData(models.Model):
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True)
    products = models.ManyToManyField('zap_catalogue.ApprovedProduct', blank=True)
    account_number = models.CharField(max_length=30, null=True, blank=True)
    account_holder = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20,null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    citrus_seller_id = models.CharField(max_length=30, null=True, blank=True)


    # def __unicode__(self):
    #     return self.full_name or self.email


class EvangeList(User):
    city = models.CharField(max_length=100, null=True, blank=True)
    commission = models.FloatField(null=True, blank=True)


class NewAppFeature(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)

    def __unicode__(self):
        return str(self.title)


class BuildNumber(models.Model):
    number = models.IntegerField()
    app = models.CharField(max_length=10, default="android")
    new_features = models.ManyToManyField('zapuser.NewAppFeature', blank=True)

    def __unicode__(self):
        return str(self.number) + ' ' + self.app


class ZapSession(models.Model):
    user = models.ForeignKey(
        'zapuser.ZapUser', related_name='zap_session')
    start_time = models.DateTimeField(auto_now_add=True)


class AppViralityKey(models.Model):
    user = models.ForeignKey(
        'zapuser.ZapUser', related_name='appvirality_key')
    key = models.CharField(max_length=50)


    def __unicode__(self):
        return '{},{},{}'.format((self.user.email or ""), (self.user.zap_username or ""), (self.key or ""))  


@receiver(post_save, sender=ZapUser)
@receiver(post_save, sender=UserProfile)
@receiver(post_save, sender=UserData)
@receiver(post_save, sender=ZapExclusiveUserData)
@receiver(post_save, sender=UserPreference)
def cache_clear(sender, instance, created, **kwargs):
    cache.clear()
    if created:
        if sender.__name__=="ZapUser":
            UserData.objects.get_or_create(user=instance)
            UserPreference.objects.get_or_create(user=instance)
            from zap_apps.extra_modules.tasks import mixpanel_task
            apply_offers_task(when="SIGNUP", user=instance.id)
            apply_offers_task(when="WEBSITE_SIGNUP", user=instance.id)
            apply_offers_task(when="APP_SIGNUP", user=instance.id)
            if settings.CELERY_USE:
                mixpanel_task.delay(instance.id, "Sign Up", "Login")
            else:
                mixpanel_task(instance.id, "Sign Up", "Login")


class WebsiteLead(models.Model):
    email = models.CharField(max_length=100, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.time)+' '+self.email


class DesignerProfile(models.Model):
    user = models.ForeignKey(
        'zapuser.ZapUser', related_name='designer_profile')
    cover_pic = models.ImageField(
        upload_to="uploads/covers/", null=True, blank=True)
    mobile_cover_pic = models.ImageField(
        upload_to="uploads/covers/", null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    description_short = models.CharField(max_length=200)

    def __unicode__(self):
        return self.user.username + str(self.user.id)


class BranchTest(models.Model):
    content = models.TextField()
    source = models.CharField(max_length=200)
