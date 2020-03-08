from django.db import models
# from zap_apps.zapuser.models import UserProfile
# Create your models here.


class Onboarding(models.Model):
    user = models.OneToOneField(
        'zapuser.ZapUser', blank=True, null=True, related_name='user_onboarding')
    #user = models.ForeignKey('zapuser.ZapUser', blank=True, null=True, related_name='user_onboarding')
    device_id = models.CharField(max_length=100, null=True, blank=True)
    task1 = models.BooleanField(default=False)
    task2 = models.BooleanField(default=False)
    task3 = models.BooleanField(default=False)
    task4 = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.user)
