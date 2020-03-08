from django.db import models

# Create your models here.


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=20, unique=True)
    coupon_description = models.CharField(
        max_length=2000, null=True, blank=True)
    perc_discount = models.FloatField(default=0, blank=True, null=True)
    abs_discount = models.FloatField(default=0, blank=True, null=True)
    max_discount = models.FloatField(blank=True, null=True)
    # coupon_owner = models.ForeignKey(Referrer)
    valid_from = models.DateTimeField()
    valid_till = models.DateTimeField()
    min_purchase = models.IntegerField(default=0)
    allowed_usage = models.FloatField(blank=True, null=True)
    allowed_per_user = models.FloatField(blank=True, null=True)
    allowed_users = models.ManyToManyField('zapuser.ZapUser', blank=True)

    def __unicode__(self):
        return unicode(self.coupon_code)



class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    code_description = models.CharField(
        max_length=2000, null=True, blank=True)
    perc_amount = models.FloatField(default=0, blank=True, null=True)
    abs_amount = models.FloatField(default=0, blank=True, null=True)
    max_amount = models.FloatField(blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_till = models.DateTimeField()
    # min_purchase = models.IntegerField(default=0)
    allowed_usage = models.FloatField(blank=True, null=True)
    allowed_per_user = models.FloatField(blank=True, null=True)
    allowed_users = models.ManyToManyField('zapuser.ZapUser', blank=True)
    allowed_emails = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.code)