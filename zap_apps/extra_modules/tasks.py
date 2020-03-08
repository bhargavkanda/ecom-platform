from celery import task
from django.conf import settings
import requests, json
from zap_apps.extra_modules.appvirality import AppViralityApi
from zap_apps.zapuser.models import AppViralityKey
from zap_apps.zapuser.models import ZapUser
from mixpanel import Mixpanel
from django.utils import timezone
from celery.task.schedules import crontab
from celery.decorators import periodic_task
mp = Mixpanel(settings.MIXPANEL_TOKEN)
import pdb
from zap_apps.order.models import Order
from django.utils import timezone
from datetime import timedelta

@task
def mixpanel_task(user_id, eventname, current_page):
    # pdb.set_trace()
    user = ZapUser.objects.get(id=user_id)
    role = user.user_type.name if (hasattr(user, "user_type") and user.user_type) else "zap_user"
    role = "Store Front" if role == 'zap_user' else "Zap User"
    platform = user.logged_device.name if (hasattr(user, "logged_device") and user.logged_device) else "website"
    platform = "Android" if platform == 'android' else "iOS" if platform == 'ios' else "Website"
    channel = user.logged_from.name if (hasattr(user, "logged_from") and user.logged_from) else "zapyle"
    channel = "Fb" if channel == 'fb' else "Insta" if channel == 'instagram' else "zapyle"
        
    mp.track(user.zap_username if hasattr(user, "zap_username") else "", 'User Event', {
        'Event Name': eventname,
        'User Type': role,
        'User Name': user.zap_username if hasattr(user, "zap_username") else "",
        'Platform': platform,
        'Channel': channel,
        'Current Page': current_page,
        'Session Start': timezone.now()
    })

@task
def del_pushbot_token(url, data, headers):
    print url, data, headers
    r = requests.put(url=url, data=data, headers=headers)
    print r.text


@task
def app_virality_conversion(u_id, conv_name, extrainfo):
    try:
        u_key = AppViralityKey.objects.get(user=u_id).key
        appvirality = AppViralityApi()
        return appvirality.conversion(u_key, conv_name, extrainfo)
    except AppViralityKey.DoesNotExist:
        pass
    except AppViralityKey.MultipleObjectsReturned:
        AppViralityKey.objects.all()[1:].delete()

@periodic_task(run_every=(crontab(minute=30, hour='4')))
def send_appvirality_conversion():
    l = []
    for i in Order.objects.filter(transaction__appvirality_done=False, delivery_date__isnull=False, delivery_date__gte=timezone.now()-timedelta(days=3)):        
        if i.delivery_date + timedelta(hours=24) > timezone.now():
            i.transaction.appvirality_done = True
            i.transaction.save()
            if settings.APPVIRALITY_ENABLE:
                app_virality_conversion(i.transaction.cart.user.id, "BuyOrSell", "Buy")
                l.append([i.transaction.cart.user.id, "BuyOrSell", "Buy"])
    return str(l)
                     
