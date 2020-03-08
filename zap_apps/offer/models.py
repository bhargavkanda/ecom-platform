from django.db import models
from django.utils import timezone
# Create your models here.


def get_remaining_time(time):
    if time > timezone.now():
        remaining_seconds = int((time - timezone.now()).total_seconds())
        remaining_days = int(remaining_seconds/86400)
        seconds_after_days = remaining_seconds - (remaining_days * 86400)
        remaining_hours = int(seconds_after_days/3600)
        seconds_after_hours = seconds_after_days - (remaining_hours * 3600)
        remaining_minutes = int(seconds_after_hours/60)
        seconds_after_minutes = seconds_after_hours - (remaining_minutes * 60)
        return {'days': remaining_days,'hours': remaining_hours, 'minutes': remaining_minutes, 'seconds': seconds_after_minutes}
    else:
        return False



def user_in_filter(filter, user_id):
    from django.http import QueryDict
    from zap_apps.filters.filters_common import cache_sort
    from zap_apps.zapuser.models import ZapUser, UserGroup
    filter_params = QueryDict(filter[unicode(filter).index('?') + 1:])  # remove ? and the part before that - send only the query part
    filter_dict = cache_sort(filter_params)
    filter_dict.pop('initial_filters')
    verdict = True
    for key in filter_dict:
        if key == 'cart_value':
            from zap_apps.cart.models import Cart
            cart = Cart.objects.get(user=user_id)
            if not cart.total_listing_price() >= filter_dict[key][0] and cart.total_listing_price() <= filter_dict[key][1]:
                return False
        elif key == 'items_count':
            from zap_apps.cart.models import Cart
            cart = Cart.objects.get(user=user_id)
            if not cart.item.all().count() >= filter_dict[key][0] and cart.item.all().count() <= filter_dict[key][1]:
                return False
        elif key.startswith('p_'):
            from zap_apps.cart.models import Cart
            from zap_apps.filters.filters_common import product_in_filter
            cart = Cart.objects.get(user=user_id)
            items = cart.item.all()
            for item in items:
                values = str(filter_dict[key])
                filter = '?' + key[2:] + '=' + values[1:len(values)-1]
                if not product_in_filter(filter, item.product):
                    return False
        elif key == 'time':
            from datetime import timedelta, datetime
            try:
                user_in_list = ZapUser.objects.filter(id=user_id)
                start_value = user_in_list.values_list(filter_dict['time'][1], flat=True)[0]
                duration = int(filter_dict['time'][0])
                if start_value <= timezone.now() and start_value+timedelta(0, duration*60, 0) >= timezone.now() and verdict==True:
                    # end_time = int((start_value.replace(tzinfo=None)+timedelta(0, duration*60, 0)-datetime(1970, 1, 1)).total_seconds() * 1000)
                    time_left = get_remaining_time(start_value+timedelta(0, duration*60, 0))
                    if time_left:
                        if time_left['days']>0:
                            verdict = str(time_left['days']) + (' day' if time_left['days']==1 else ' days')
                        elif time_left['hours']>0:
                            verdict = str(time_left['hours']) + (' hour' if time_left['hours'] == 1 else ' hours')
                        elif time_left['minutes']>0:
                            verdict = str(time_left['minutes']) + (' minute' if time_left['minutes'] == 1 else ' minutes')
                        else:
                            verdict = str(time_left['seconds']) + ' seconds'
                    else:
                        verdict = False
                else:
                    return False
            except Exception:
                return False
        elif key == 'user_group':
            local_verdict = False
            user_groups = UserGroup.objects.filter(id__in=list(filter_dict['user_group']))
            user = ZapUser.objects.get(id=user_id)
            if user_groups.filter(zapyle_users=user):
                local_verdict = True
            if user.email:
                if user_groups.filter(emails__icontains=user.email):
                    local_verdict = True
            if user.phone_number:
                if user_groups.filter(phone_numbers__icontains=user.phone_number):
                    local_verdict = True
            if not local_verdict:
                return False
    return verdict

class OfferBenefit(models.Model):
    TYPE_CHOICES = (
        ('CREDIT', "This much give as credit"),
        ('PERCENTAGE_COMMISSION', "This much percentage taken by zapyle"),
        ('PERCENTAGE_DISCOUNT', "This much percentage off on purchase"),
        ('ABS_DISCOUNT', "Amount off on purchase in Rupees"),
        ('CAMPAIGN_DISCOUNT', "Gives % off based on the campaign product"),
    )
    DISCOUNT_CHOICES = (
        ('PRODUCT', "The discount is given on each product in the Cart"),
        ('CART', "The discount is given overall on the Cart"),
    )
    type = models.CharField(
        choices=TYPE_CHOICES, default='CREDIT', max_length=30)
    value = models.FloatField(default=0, blank=True, null=True)
    PERCENTAGE_CHOICES = (
        ('total_value', 'Total Value'),
        ('least_product', 'Product with least price'),
    )
    max_limit = models.FloatField(blank=True, null=True)
    discount_on = models.CharField(choices=DISCOUNT_CHOICES, default='PRODUCT', max_length=30)
    percentage_on = models.CharField(max_length=30, choices=PERCENTAGE_CHOICES, default='total_value')

    def __unicode__(self):
        return unicode(self.type + " {}".format(self.value))


class OfferCondition(models.Model):
    name = models.CharField(max_length=100)
    product_filter = models.CharField(max_length=100, blank=True, null=True, help_text='parameters same as the ones used'
                                                                                       ' in Banner Actions')
    user_filter = models.CharField(max_length=100, blank=True, null=True,
                                   help_text='Supported parameters - item_count; user_group; cart_value; '
                                             'p_[product property] - eg: p_price, p_brand etc;  time - time limits for user'
                                             ' like 3 hours from sign up, 2 hours from adding to cart etc.') # '?cart_items=1&time=data_joined,180&user_group=2'

    def __unicode__(self):
        return self.name

class CustomManager(models.Manager):
    def get_queryset(self):
        return super(CustomManager, self).get_queryset()

class ValidOfferManager(models.Manager):
    def get_queryset(self):
        return super(ValidOfferManager, self).get_queryset().filter(start_time__lt=timezone.now(), end_time__gt=timezone.now(), status=True)


class ZapOffer(models.Model):
    OFFER_TYPE_CHOICES = (
        ('SITE', "Shows the offer to all users"),
        ('RESTRICTED', "Shows the offer to only applicable users."),
        ('HIDDEN', "Do not show on website."),
    )
    OFFER_WHEN = (
        ('ADD_CART', "offer when a product is added to cart"),
        # ('LISTING', "apply when uploading product"),
        ('SIGNUP', "apply on signup"),
        ('APP_SIGNUP', "apply on mobile signup"),
        ('WEBSITE_SIGNUP', "apply on website signup"),
    )
    code = models.CharField(max_length=30, unique=True, help_text="Mandatory if the Offer type is Coupon", blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    offer_type = models.CharField(
        choices=OFFER_TYPE_CHOICES, default='SITE', max_length=20)
    offer_when = models.CharField(
        choices=OFFER_WHEN, default='ADD_CART', max_length=20)
    status = models.BooleanField(default=False)
    show_timer = models.BooleanField(default=False)
    usage_per_user = models.IntegerField(default=0, help_text="If the value is 0, the Offer can be used unlimited times")
    offer_benefit = models.ForeignKey('offer.OfferBenefit', related_name='zapoffer')
    offer_condition = models.ForeignKey('offer.OfferCondition', related_name='zapoffer', null=True, blank=True)
    objects = CustomManager()
    valid_objects = ValidOfferManager()
    def __unicode__(self):
        return unicode(((self.code + '  :  ') if self.code else '') + self.name)

    @property
    def offer_on(self):
        return self.offer_benefit.discount_on

    def offer_available(self):
        if self.status and (self.start_time < timezone.now() < self.end_time):
            return True
        return False

    def offer_available_on_product(self, product_id):
        from zap_apps.zap_catalogue.models import ApprovedProduct
        from zap_apps.filters.filters_common import product_in_filter
        try:
            product = ApprovedProduct.objects.get(id=product_id)
            if self.status and (self.start_time < timezone.now() < self.end_time):
                if self.offer_condition:
                    condition = self.offer_condition
                    if condition.product_filter:
                        return product_in_filter(condition.product_filter, product)
                    else:
                        return True
                else:
                    return True
            else:
                return False
        except Exception:
            return False

    def offer_available_for_user(self, user_id):
        if self.usage_per_user > 0:
            from zap_apps.order.models import Transaction, Order
            if self.offer_on == 'PRODUCT':
                if Order.objects.filter(transaction__buyer__id=user_id, offer=self.id).count() +\
                        Item.objects.filter(cart__user__id=user_id, offer=self.id).count() < self.usage_per_user:
                    return True
                else:
                    return False
            elif self.offer_on == 'CART':
                if Transaction.objects.filter(buyer__id=user_id, offer=self.id).count() < self.usage_per_user:
                    return True
                else:
                    return False
        if self.status and (self.start_time < timezone.now() < self.end_time):
            if self.offer_condition:
                condition = self.offer_condition
                if condition.user_filter:
                    return user_in_filter(condition.user_filter, user_id)
                else:
                    return True
            else:
                return True
        else:
            return False

    def get_benefit(self, id):
        from zap_apps.zap_catalogue.models import ApprovedProduct
        from zap_apps.marketing.models import CampaignProducts
        if self.offer_on == 'PRODUCT':
            try:
                discount = 0
                product = ApprovedProduct.ap_objects.get(id=id)
                if hasattr(self, 'campaign'):
                    campaign_product = CampaignProducts.objects.get(products=product.id, campaign=self.campaign)
                    discount = round(product.listing_price * campaign_product.discount / 100)
                else:
                    benefit = self.offer_benefit
                    if benefit.type == 'PERCENTAGE_DISCOUNT':
                        discount = round(product.listing_price * benefit.value / 100)
                        if benefit.max_limit:
                            if discount > benefit.max_limit:
                                discount = benefit.max_limit
                    elif benefit.type == 'ABS_DISCOUNT':
                        discount = benefit.value
                return discount
            except Exception:
                return 0
        elif self.offer_on == 'CART':
            from zap_apps.cart.models import Cart
            try:
                discount = 0
                cart = Cart.objects.get(user=id)
                benefit = self.offer_benefit
                if benefit.type == 'PERCENTAGE_DISCOUNT':
                    if benefit.percentage_on == 'total_value':
                        discount = round(cart.total_listing_price() * benefit.value / 100)
                    elif benefit.percentage_on == 'least_product':
                        least_price = min([item.selling_price for item in cart.item.all()])
                        discount = round(least_price * benefit.value / 100)
                    if benefit.max_limit:
                        if discount > benefit.max_limit:
                            discount = benefit.max_limit
                elif benefit.type == 'ABS_DISCOUNT':
                    discount = benefit.value
                return discount
            except Exception:
                return 0

    def is_applicable(self, product_id=None, user_id=None):
        if self.offer_available():
            if self.offer_on == 'CART':
                from zap_apps.cart.models import Cart
                if user_id:
                    if Cart.objects.get(user=user_id).is_empty():
                        return {'status': False, 'error': 'The cart can not be empty.'}
                else:
                    return {'status': False, 'error': 'Please login to apply this coupon.'}
            if self.usage_per_user > 0:
                if user_id:
                    if not self.offer_available_for_user(user_id):
                        return {'status': False,
                                'error': 'Sorry! This offer is restricted to certain users. Please write to hello@zapyle.com in case of any queries.'}
                else:
                    return {'status': False, 'error': 'Please login to apply this coupon.'}
            if self.offer_condition:
                condition = self.offer_condition
                if condition.product_filter:
                    if product_id:
                        if not self.offer_available_on_product(product_id):
                            return {'status': False, 'error': 'Sorry! Offer not applicable on this product. Please write to hello@zapyle.com in case of any queries.'}
                    else:
                        return {'status': False, 'error': 'This offer can be applied only on certain products.'}
                if condition.user_filter:
                    if user_id:
                        if not self.offer_available_for_user(user_id):
                            return {'status': False, 'error': 'Sorry! This offer is restricted to certain users. Please write to hello@zapyle.com in case of any queries.'}
                    else:
                        return {'status': False, 'error': 'Please login to apply this coupon.'}
                return {'status': True}
            else:
                return {'status': True}
        else:
            return {'status': False, 'error': 'This offer has expired.'}

    def validity(self, user_id=None):
        from datetime import datetime
        try:
            if user_id and str(self.offer_condition.user_filter).find('time=') > -1:
                validity = self.offer_available_for_user(user_id)
            else:
                # validity = int((self.end_time.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()) * 1000
                time_left = get_remaining_time(self.end_time)
                if time_left:
                    if time_left['days'] > 0:
                        validity = str(time_left['days']) + (' day' if time_left['days'] == 1 else ' days')
                    elif time_left['hours'] > 0:
                        validity = str(time_left['hours']) + (' hour' if time_left['hours'] == 1 else ' hours')
                    elif time_left['minutes'] > 0:
                        validity = str(time_left['minutes']) + (' minute' if time_left['minutes'] == 1 else ' minutes')
                    else:
                        validity = str(time_left['seconds']) + ' seconds'
                else:
                    validity = False
        except Exception:
            # validity = int((self.end_time.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()) * 1000
            time_left = get_remaining_time(self.end_time)
            if time_left:
                if time_left['days'] > 0:
                    validity = str(time_left['days']) + (' day' if time_left['days'] == 1 else ' days')
                elif time_left['hours'] > 0:
                    validity = str(time_left['hours']) + (' hour' if time_left['hours'] == 1 else ' hours')
                elif time_left['minutes'] > 0:
                    validity = str(time_left['minutes']) + (' minute' if time_left['minutes'] == 1 else ' minutes')
                else:
                    validity = str(time_left['seconds']) + ' seconds'
            else:
                validity = False
        return validity

class ZapCredit(models.Model):
    user = models.ForeignKey(
        'zapuser.ZapUser', related_name='zap_credit')
    amount = models.IntegerField(default=0)
    credit = models.BooleanField(default=True)
    purpose = models.CharField(max_length=50, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    tr_ref_id = models.CharField(max_length=30, null=True, blank=True)
    # rewarddtlid = models.CharField(max_length=30, null=True, blank=True)
    def __unicode__(self):
        return unicode(("credit" if self.credit else "debit") + "--{}--{}".format(self.amount, self.user.email or ""))