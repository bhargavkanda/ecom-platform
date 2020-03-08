from celery import task
from zap_apps.zapuser.models import ZapUser
from django.conf import settings
from zap_apps.zap_notification.views import ZapEmail, PushNotification, ZapSms
from zap_apps.zap_notification.models import Notification
from django.utils import timezone









@task
def after_admire_notif(user_id,current_user_id):
    # from zap_apps.zap_catalogue.models import Loves
    pushnots = PushNotification()
    try:
        user = ZapUser.objects.get(id=user_id)
        if current_user_id in user.profile.admiring.all().values_list('id',flat=True):
            current_user = ZapUser.objects.get(id=current_user_id)
            notif = Notification.objects.filter(user=user,notified_by=current_user,message=(
                    current_user.zap_username or current_user.get_full_name()) + " admired you.",action="ad")
            if notif:
                if ((timezone.now() - notif.first().notif_time).seconds)/60 > 2:
                    pushnots.send_notification(
                        user, (current_user.zap_username or current_user.get_full_name()) + " admired you.")
                    Notification.objects.create(user=user, notified_by=current_user, message=(
                        current_user.zap_username or current_user.get_full_name()) + " admired you.", action="ad")
            else:
                pushnots.send_notification(
                    user, (current_user.zap_username or current_user.get_full_name()) + " admired you.")
                Notification.objects.create(user=user, notified_by=current_user, message=(
                    current_user.zap_username or current_user.get_full_name()) + " admired you.", action="ad")
    except:
        print "No User"

