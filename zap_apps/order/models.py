from django.db import models
from django.db.models import Sum, F, FloatField
from django.conf import settings
import pdb
from django.utils import timezone
# from zap_apps.zap_catalogue.models import Product
# Create your models here.

RETURN_REASONS = (
    ('0', 'The product is not in the size I ordered'),
    ('1', 'The product is damaged'),
    ('2', 'The product is not as described'),
    ('3', 'The product is a replica'),
    ('4', 'Other'),
)
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
VERIFICATION = (
    ('approved', 'verification approved'),
    ('rejected', 'verification rejected'),
    ('rejected_shipped', 'rejected item shipped back'),
)
TRANSFER_MODE = (
    ('account_transfer','Account Transfer'),
    ('zapcash','Zap Wallet')
    )
# class MVCWallet(models.Model):
#     user = models.ForeignKey('zapuser.ZapUser', related_name='mvc')
#     amount = models.FloatField(default=0)

# class CustomManager(models.Manager):
#     def get_queryset(self):
#         return super(CustomManager, self).get_queryset().exclude(deleted=True)


class Transaction(models.Model):
    PAYMENT_MODE = (
        ('debit_card', 'Debit Card'),
        ('credit_cart', 'Credit Card'),
        ('cod', 'Cash on delivery'),
        ('netbanking', 'Netbanking'),
        ('juspay', 'Juspay'),
        ('wallet', 'Using wallet Only'),
        ('emi', 'EMI'))
    buyer = models.ForeignKey('zapuser.ZapUser', related_name='buyer')
    payment_mode = models.CharField(choices=PAYMENT_MODE, null=True, blank=True, max_length=30)
    time = models.DateTimeField(auto_now_add=True, editable=True)
    transaction_ref = models.CharField(max_length=30, null=True, blank=True)
    appvirality_done = models.BooleanField(default=False)
    zapwallet_used = models.FloatField(null=True, blank=True, default=0)
    status = models.CharField(choices=(('success', 'SUCCESS'), ('on_hold', 'FORWARDED'),('failed', 'FAILED'),('sig_mismatch', 'signature mismatch')), max_length=20, null=True, blank=True)
    # completed = models.BooleanField(default=False)
    consignee = models.ForeignKey('address.Address', related_name='trans_buyer',null=True, blank=True)
    final_price = models.FloatField(default=0)
    platform = models.CharField(max_length=10, null=True, blank=True)
    offer = models.ForeignKey('offer.ZapOffer', null=True, blank=True, on_delete=models.SET_NULL, related_name='applied_transaction')
    # deleted = models.BooleanField(default=False)
    # objects = CustomManager()

    def ordered_products(self):
        return OrderedProduct.objects.filter(order__transaction=self)

    def original_price(self):
        return OrderedProduct.objects.filter(
            order__transaction=self).aggregate(
            price=Sum(
                F('original_price')*F('order__quantity'
                    ),output_field=FloatField()
                )
            )['price']

    @property
    def listing_price(self):
        return OrderedProduct.objects.filter(
            order__transaction=self).aggregate(
            price=Sum(
                F('listing_price')*F('order__quantity'
                    ),output_field=FloatField()
                )
            )['price']

    def shipping_charge(self):
        return OrderedProduct.objects.filter(
            order__transaction=self).aggregate(
            price=Sum(
                F('order__shipping_charge')
                )
            )['price']
    def total_price_with_shipping_charge(self):
        return self.listing_price + self.shipping_charge()

    def __unicode__(self):
        return unicode(self.id) + ". Buyer - " + unicode(self.buyer)



class OrderedProduct(models.Model):
    image = models.ForeignKey('zap_catalogue.ProductImage', blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    style = models.CharField(null=True, blank=True, max_length=30)
    brand = models.CharField(null=True, blank=True, max_length=30)
    original_price = models.FloatField(null=True, blank=True)
    size = models.CharField(max_length=30, null=True, blank=True)
    listing_price = models.FloatField(null=True, blank=True)
    occasion = models.CharField(null=True, blank=True, max_length=30)
    product_category = models.CharField(null=True, blank=True, max_length=30)
    age = models.CharField(max_length=30, null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    condition = models.CharField(null=True, blank=True, max_length=30)
    # discount = models.FloatField(null=True, blank=True)
    percentage_commission = models.FloatField(default=25)
    with_zapyle = models.BooleanField(default=False)

    @property
    def shipping_charge(self):
        return self.order.shipping_charge


    @property
    def quantity(self):
        return self.order.quantity
    def save(self, *args, **kwargs):
        if (self.original_price and self.listing_price):
            self.discount = (float(self.original_price) - float(
                            self.listing_price)) / float(self.original_price)
        super(OrderedProduct, self).save(*args, **kwargs)


    def __unicode__(self):
        return self.title
ORDER_STATUS = (
    ('pending', 'Order is pending.'),
    ('failed', 'Order failed.'),
    ('being_confirmed', 'Order being processed.'),
    ('cancelled', 'Order is cancelled.'),
    ('confirmed', 'Order is confirmed'),
    ('being_made', 'In the making'),
    ('made','Product made to order'),
    ('pickup_in_process', 'Pickup in Process'),
    ('picked_up', 'Product picked up'),
    ('verification', 'Checking Authenticity'),
    ('product_approved', 'Product Approved.'),
    ('product_rejected', 'Product Rejected'),
    ('on_the_way_to_you', 'On the way'),
    ('delivered', 'Delivered'),
    ('on_hold', 'On hold'),
    ('return_requested', 'Return Requested'),
    ('return_in_process','Return is in process'),
    ('return_shipped', 'shipped to seller'),
    ('returned','Return Completed'))


PAYOUT_STATUS = (
    ('can_initiate_payout', 'Now payout can start.'),
    ('paid_out', 'Seller go money now.'))
REFUND_STATUS = (
    ('initiated','refund being called or emailed'),
    ('refunded', 'Refund completed')
    )


class Order(models.Model):

    product = models.ForeignKey('zap_catalogue.ApprovedProduct', related_name='product', null=True, blank=True)
    ordered_product = models.OneToOneField('order.OrderedProduct', related_name='order', null=True, blank=True)
    transaction = models.ForeignKey('order.Transaction', related_name='order')
    order_number = models.CharField(max_length=30, unique=True)
    payout_status = models.CharField(choices=PAYOUT_STATUS, null=True, blank=True, max_length=30)
    quantity = models.IntegerField(default=1)
    final_price = models.FloatField(blank=True, null=True)
    shipping_charge = models.FloatField(default=settings.SHIPPING_CHARGE)
    # cancelled = models.BooleanField(default=False)
    # returned = models.BooleanField(default=False)
    order_status = models.CharField(choices=ORDER_STATUS, default="being_confirmed", max_length=30)
    consignor = models.ForeignKey('address.Address', related_name='order_seller',null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    confirmed_with_buyer = models.BooleanField(default=False)
    confirmed_with_seller = models.BooleanField(default=False)
    placed_at = models.DateTimeField(auto_now_add=True, editable=False)
    service_invoice_no = models.CharField(max_length=30, null=True, blank=True)
    zapwallet_used = models.FloatField(null=True, blank=True, default=0)
    offer = models.ForeignKey('offer.ZapOffer', blank=True, null=True, on_delete=models.SET_NULL)
    product_verification = models.CharField(choices=VERIFICATION, null=True, blank=True, max_length=20)
    payout_mode = models.CharField(max_length=20, choices=TRANSFER_MODE, null=True, blank=True)
    refund_status = models.CharField(choices=REFUND_STATUS, max_length=20, null=True, blank=True)
    rating = models.IntegerField(blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     print ">>>"
    #     self.shipping_charge = settings.SHIPPING_CHARGE if self.product.listing_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0
    #     super(Order, self).save(*args, **kwargs)

    def final_payable_price(self):
        return float(self.final_price * self.quantity) + float(self.shipping_charge) - self.zapwallet_used

    def total_price(self):
        return float(self.final_price * self.quantity) + float(self.shipping_charge)

    def __unicode__(self):
        return unicode(self.id) + ". Buyer - " + unicode(self.transaction.buyer.email) + " " + unicode(self.ordered_product.title)


class Return(models.Model):

    order_id = models.OneToOneField('order.Order', related_name='returnmodel')
    reason = models.CharField(max_length=100, choices=RETURN_REASONS)
    consignee = models.ForeignKey('address.Address', related_name='seller',null=True, blank=True)
    consignor = models.ForeignKey('address.Address', related_name='buyer',null=True, blank=True)
    # logistics_owner = models.CharField(max_length=10, null=True, blank=True)
    # pickup_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    # value = models.FloatField()
    requested_at = models.DateTimeField(auto_now_add=True, editable=False)
    refund_mode = models.CharField(max_length=20, choices=TRANSFER_MODE, null=True, blank=True)
    last_communication = models.DateTimeField(null=True, blank=True)
    # approved_zapcash = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    # credited = models.BooleanField(default=False)
    self_return = models.BooleanField(default=False)
    # triggered_logistics = models.BooleanField(default=False)
    product_verification = models.CharField(choices=VERIFICATION, null=True, blank=True, max_length=20)
    return_status = models.CharField(choices=ORDER_STATUS, default="being_confirmed", max_length=30)

    def __unicode__(self):
        return unicode(self.id) + ". Order ID - " + unicode(self.order_id.id)

class OrderTracker(models.Model):
    orders = models.ForeignKey('order.Order', related_name='track_order', null=True, blank=True)
    returns = models.ForeignKey('order.Order', related_name='track_return', null=True, blank=True)
    time =  models.DateTimeField(default=timezone.now)
    status = models.CharField(choices=ORDER_STATUS, max_length=30)
    def __unicode__(self):
        return unicode(self.orders) + " - " + unicode(self.status)
