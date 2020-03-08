from django.db import models

# Create your models here.


class UserData(models.Model):
    user = models.OneToOneField('zapuser.ZapUser', related_name='user')
    code = models.CharField(max_length=10)
    perc_commission = models.FloatField(default=1.0)

    def __unicode__(self):
        return unicode(self.code) + ". Buyer - " + unicode(self.user.first_name)

class RefCode(models.Model):
    code = models.CharField(max_length=20)
    users = models.ManyToManyField(
        'zapuser.ZapUser', blank=True)
    def __unicode__(self):
        return unicode(self.code)