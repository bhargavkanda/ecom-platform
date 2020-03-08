import sys,os
# sys.path.append("/path/to/project")
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.local"
django.setup()

from django.utils import timezone
from zap_apps.marketing.models import *
from zap_apps.zapuser.models import ZapUser, ZAPGCMDevice
import random
from zap_apps.zap_notification.bulk_push_notif import send_to_queue

notif = Notifs.objects.filter(action__action_type='filtered')[0]
msg = notif.text
sent_time = timezone.now()

user = ZapUser.objects.filter(zap_username='Skkrish')
users = [i.id for i in ZAPGCMDevice.objects.filter(user__zapuser__in=user)]
ios_users = ZAPGCMDevice.objects.filter(id__in=users, logged_device__name="ios", active=True).exclude(user__zapuser__zap_username=None).distinct()
ios_reg_id_list = ios_users.values_list('registration_id', flat=True)

extra = {
        'action': 'filtered',
        'args': notif.action.get_args_string()
    }
extra['marketing'] = True

extra['notif_id'] = str(notif.id)
extra['sent_time'] = str(sent_time)

extra = {k: str(v) for k, v in extra.items()}
extra.update({"message":msg})
extra['random_num'] = str(random.choice(range(100)))
send_to_queue(extra, ios_reg_id_list, 'dev.zapyle.com', 'ios')
print 'ok'