from django.db import models
from zap_apps.zapuser.models import ZapUser
# Create your models here.

ACTION_CHOICE = (
    ('ap', 'approve'),
    ('lo', 'love'),
    ('ad', 'admire'),
    ('co', 'comment'))


class Notification(models.Model):
    user = models.ForeignKey('zapuser.ZapUser', null=True,blank=True, related_name='notification')
    action = models.CharField(choices=ACTION_CHOICE,default="lo", max_length=2)
    notified_by = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, related_name='notifications')
    message = models.TextField()
    notif_time = models.DateTimeField(auto_now_add=True, editable=False)
    product = models.ForeignKey('zap_catalogue.ApprovedProduct', null=True, blank=True)
    seen = models.BooleanField(default=False)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-notif_time']

    def __unicode__(self):
        return str(self.message)