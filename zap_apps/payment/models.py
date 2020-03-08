from django.db import models
from django.db.models import Sum, F

MODE_CHOICES = (
        ('0', "Affiliate"),
        ('1', "Promo"),
        ('2', "Return"),
    )

# Create your models here.


class TimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class ZapWallet(TimeModel):
    credit = models.BooleanField(default=False)
    user = models.ForeignKey('zapuser.ZapUser', related_name='zapcash_user1')
    transaction = models.ForeignKey(
        'order.Transaction', related_name='transaction_id1', null=True, blank=True)
    amount = models.FloatField()
    # zapcash_transId = models.CharField(max_length=20, null=True, blank=True)
    return_id = models.ForeignKey(
        'order.Return', related_name='return_id1', null=True, blank=True)
    mode = models.CharField(
        choices=MODE_CHOICES, default='0', max_length=3)
    promo = models.ForeignKey('coupon.PromoCode', related_name='promo_code', null=True, blank=True)
    purpose = models.CharField(max_length=50, null=True, blank=True)
    # withdrawable = models.BooleanField(default=False)
    # status = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.amount) + " " + (" credit | " if self.credit else " debit | ") + unicode(self.user)+ " | " + unicode(self.purpose) + " | Total : " + unicode(get_total_wallet(self.user))


def get_total_wallet(user):
    return (ZapWallet.objects.filter(user=user, credit=True).aggregate(s=Sum(F('amount')))['s'] or 0) - (ZapWallet.objects.filter(user=user, credit=False).aggregate(s=Sum(F('amount')))['s'] or 0)


# CITRUS PAYMENT RESPONSE
class PaymentResponse(TimeModel):
    transaction = models.ForeignKey('order.Transaction', related_name='payment_response')
    payment_success = models.BooleanField(default=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_transaction_id = models.CharField(
        max_length=40, null=True, blank=True)
    transaction_ref_id = models.CharField(max_length=40, null=True, blank=True)
    pg_transaction_id = models.CharField(max_length=40, null=True, blank=True)

    status = models.CharField(max_length=50, null=True, blank=True)
    payment_gateway = models.CharField(max_length=40, null=True, blank=True)
    amount = models.CharField(max_length=10, null=True, blank=True)
    payment_mode = models.CharField(max_length=20, null=True, blank=True)
    payment_trial_no = models.IntegerField(default=1, null=True, blank=True)

    marketplaceTxId = models.CharField(max_length=20, null=True, blank=True)

    currency = models.CharField(max_length=8, null=True, blank=True)
    fees = models.CharField(max_length=15, null=True, blank=True)
    payment_time = models.CharField(max_length=30, null=True, blank=True)
    whole_response = models.CharField(max_length=4000, null=True, blank=True)
    error_message = models.CharField(max_length=200, null=True, blank=True)

    issuer_ref_no = models.CharField(max_length=20,null=True,blank=True)
    auth_id_code = models.CharField(max_length=15,null=True,blank=True)
    currency = models.CharField(max_length=10,null=True,blank=True)
    merchant_transaction_id = models.CharField(max_length=30,null=True,blank=True)

    def __unicode__(self):
        return unicode(self.transaction.id) + "  " + unicode(self.status)


class Payout(TimeModel):
    seller = models.ForeignKey('zapuser.ZapUser', related_name='payout')
    order = models.ForeignKey('order.Order', related_name='order')
    # marketplace_transId = models.CharField(
    #     max_length=20, null=True, blank=True)
    # split_id = models.CharField(max_length=20, null=True, blank=True)
    # release_fund_ref = models.CharField(max_length=20, null=True, blank=True)
    payout_status = models.BooleanField(default=False)
    total_value = models.FloatField(null=True, blank=True)
    seller_cut = models.FloatField(null=True, blank=True)
    zapyle_cut = models.FloatField(null=True, blank=True)
    error_message = models.CharField(max_length=3000, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.marketplace_transId) + " " + unicode(self.payout_status)


class RefundResponse(TimeModel):
    TRASNFER_MODE = (
        ('citrus', 'Refunded via citrus api'),
        ('manual', 'Refunded manually via zapyle')
        )
    order = models.ForeignKey('order.Order', related_name='order_refund')
    amount = models.CharField(max_length=10, default=0)
    mode = models.CharField(choices=TRASNFER_MODE, max_length=10, default='citrus')
    whole_response = models.CharField(max_length=4000, null=True, blank=True)


class BillGeneratorModel(models.Model):
    merchant_transaction_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    request_signature = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
