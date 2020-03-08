from django.db import models
# import zap_apps.zapuser.models
# from zap_apps.zapuser.models import ZapUser

# Create your models here.


class State(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.name)


class Address(models.Model):
    user = models.ForeignKey('zapuser.ZapUser')
    name = models.CharField(max_length=50)
    address = models.TextField()
    address2 = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.ForeignKey('address.State')
    country = models.CharField(max_length=30, default='India')
    phone = models.CharField(max_length=20)
    pincode = models.CharField(max_length=20)
    # email = models.EmailField(max_length=50)

    def __unicode__(self):
        return unicode(self.user) + " " + unicode(self.name)


class CityPincode(models.Model):
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)

    def __unicode__(self):
        return unicode(self.pincode)