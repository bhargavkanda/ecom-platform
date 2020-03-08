from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from datetime import timedelta, datetime
from celery import task
from zap_apps.marketing.marketing_data_serializer import *
from zap_apps.zap_analytics.tasks import track_notification
from zap_apps.zap_notification.models import Notification
from zap_apps.zapuser.models import ZapUser
from zap_apps.zap_notification.views import PushNotification
from zap_apps.marketing.models import *
from django.conf import settings
from dateutil import parser
from zap_apps.zapuser.models import ZAPGCMDevice
from zap_apps.zap_notification.tasks import gcm_multi_task
from django.db.models.query import QuerySet
from zap_apps.zap_catalogue.models import ApprovedProduct


@task
def marketing_send_notif(notif, users):
    # pdb.set_trace()
    sent_time = timezone.now()
    data = {}
    if notif.action.action_type == 'own_profile':
        own_profile_list = []
        for user in users:
            data = {
                'action': 'profile',
                'profile_id': user.id,
                'profile_name': user.zap_username,
                'profile_type': user.user_type.name,
                'profile_pic': user.profile.profile_pic,
                'marketing': True,
                'notif_id': str(notif.id),
                'sent_time': str(sent_time),
                'image': settings.CURRENT_DOMAIN + notif.image.url
            }
            data = {k: str(v) for k, v in data.items()}
            own_profile_list.append({'zap_username': user.zap_username, 'text': notif.text, 'data': data})
        # save tracker
        if settings.CELERY_USE:
            save_notification_tracker.delay(users.values_list('id', flat=True), notif.id, sent_time, 'marketing')
            own_profile_push_notif.apply_async(args=[own_profile_list], countdown=300)
        else:
            save_notification_tracker(users.values_list('id', flat=True), notif.id, sent_time, 'marketing')
            own_profile_push_notif(own_profile_list)
    else:
        if notif.action.action_type == 'filtered':
            data = {
                'action': 'filtered',
                'args': notif.action.get_args_string()
            }
            print(data)
        elif notif.action.action_type == 'product':
            product = ApprovedProduct.ap_objects.get(id=notif.action.data['id'])
            data = {
                'action': 'product',
                'product_id': product.id,
                'product_title': product.title,
                'product_img_url': product.images.all()[0].image.url_100x100,
                'product_sale': product.get_sale_display(),

            }
            print(data)
        elif notif.action.action_type == 'profile':
            profile = ZapUser.objects.get(id=notif.action.data['id'])
            data = {
                'action': 'profile',
                'profile_id': profile.id,
                'profile_name': profile.zap_username,
                'profile_type': profile.user_type.name,
                'profile_pic': profile.profile.profile_pic
            }
            print(data)
        elif notif.action.action_type == 'newsfeed':
            data = {
                'action': 'newsfeed'
            }
            print(data)
        elif notif.action.action_type == 'upload':
            data = {
                'action': 'upload'
            }
            print(data)
        elif notif.action.action_type == 'earn_cash':
            data = {
                'action': 'earn_cash'
            }
        elif notif.action.action_type == 'update_app':
            data = {
                'action': 'update_app'
            }
        elif notif.action.action_type == 'deep_link':
            data = {
                'action' : 'deep_link',
                'target' : 'http://go.zapyle.com/WxOl/XlqVQE3gAy'
            }
        data['marketing'] = True
        if notif.image:
            data['image'] = settings.CURRENT_DOMAIN + notif.image.url
        data['notif_id'] = str(notif.id)
        data['sent_time'] = str(sent_time)

        data = {k: str(v) for k, v in data.items()}
        # if data_recieved['type'] == 'AllUsers':
        username_list = ZapUser.objects.filter(id__in=users).values_list('zap_username', flat=True)
        if settings.CELERY_USE:
            save_notification_tracker.delay(users.values_list('id', flat=True), notif.id, sent_time, 'marketing')
            send_delayed_notification.apply_async(args=[username_list, notif.text, data], countdown=2)
        else:
            save_notification_tracker(users.values_list('id', flat=True), notif.id, sent_time, 'marketing')
            send_delayed_notification(username_list, notif.text, data)


@task
def own_profile_push_notif(own_profile_list):
    # pdb.set_trace()
    for notif in own_profile_list:
        send_delayed_notification(notif['zap_username'], notif['text'], notif['data'])


def nurture_1_30():
    nuture_cond = Condition.objects.filter(condition_type='0')
    notifs = Notifs.objects.filter(condition__in=nuture_cond)
    notif_srlzr = NotifsSerializer(notifs, many=True)
    # Create a finder
    notifs_finder = {}
    dummy_date = datetime(2016, 1, 1)

    for notif in notif_srlzr.data:
        notifs_finder.update({notif['condition'][0]['value'][0]: notif})

    program_start_date = datetime(2016, 3, 18, 23, 20, 59, 742985)
    old_users = ZapUser.objects.filter(date_joined__lte=program_start_date)

    new_users = ZapUser.objects.filter(date_joined__gte=program_start_date).filter(
        date_joined__gte=timezone.now() - timedelta(days=30))

    # Send Push notif to all old users based on (today-startdate).day
    old_user_notif = notifs_finder.get((timezone.now().date() - program_start_date.date()).days, None)
    p = PushNotification()
    if old_user_notif:
        # pdb.set_trace()
        if old_user_notif.scheduled_time:

            current = timezone.now().time()
            scheduled_time = parser.parse(old_user_notif.scheduled_time).time()
            diff_time = datetime.combine(dummy_date, scheduled_time) - datetime.combine(dummy_date, current)

            # pdb.set_trace()
            if settings.CELERY_USE:
                marketing_send_notif.apply_async(args=[old_user_notif, old_users], countdown=diff_time.seconds)
            else:
                marketing_send_notif(old_user_notif, old_users)
        else:
            marketing_send_notif(old_user_notif, old_users)
            # marketting_send_notif(old_user_notif,old_users)
    new_user_finder = {}
    for user in new_users:
        if new_user_finder.get((timezone.now() - user.date_joined).days, None):
            new_user_finder[(timezone.now() - user.date_joined).days].append(user)
        else:
            new_user_finder.update({(timezone.now() - user.date_joined).days: [user]})
    # pdb.set_trace()
    for x, y in new_user_finder.items():
        notif = notifs_finder.get(x, None)
        if notif:
            print(y)
            if notif.scheduled_time:
                current = timezone.now().time()
                scheduled_time = parser.parse(old_user_notif.scheduled_time).time()
                diff_time = datetime.combine(dummy_date, scheduled_time) - datetime.combine(dummy_date, current)
                if settings.CELERY_USE:
                    marketing_send_notif.apply_async(args=[notif, y], countdown=diff_time.seconds)
                else:
                    marketing_send_notif(notif, y)
            else:
                marketing_send_notif(notif, y)
                # marketing_send_notif(notif,y)


@task
def save_notification_tracker(users, notif_id, sent_time, notif_type):
    # pdb.set_trace()
    users = ZapUser.objects.filter(id__in=users)
    notif = Notifs.objects.get(id=notif_id)
    # for user in users:
    track = [
        NotificationTracker(user=user, notif=notif, notif_type=notif_type, sent_time=sent_time.replace(tzinfo=None)) for
        user in users]
    NotificationTracker.objects.bulk_create(track)


@task
def send_delayed_notification(user, msg, extra=None):
    # pdb.set_trace()
    if settings.PUSH_NOTIFICATION_ENABLE:
        # pdb.set_trace()
        if not (isinstance(user, list) or isinstance(user, QuerySet)):
            user = [user]
        user = ZapUser.objects.filter(zap_username__in=user)
        # if settings.CELERY_USE:
        #     gcm_task.delay([i.id for i in ZAPGCMDevice.objects.filter(logged_device__name="android", user__zapuser__in=user)], msg, extra=extra)
        # else:

        # gcm_multi_task(ZAPGCMDevice.objects.filter(user__zapuser__in=user), msg, extra=extra)
        if settings.CELERY_USE:
            gcm_multi_task.delay([i.id for i in ZAPGCMDevice.objects.filter(user__zapuser__in=user)], msg, extra=extra)
        else:
            gcm_multi_task([i.id for i in ZAPGCMDevice.objects.filter(user__zapuser__in=user)], msg, extra=extra)


def get_notification_tracking_data(notification_id, user, sent_time, open_time, platform, notification_type):
    notification_tracker = NotificationTracker.objects.get(notif_id=notification_id, user=user, sent_time=sent_time,
                                                           opened_time=open_time)
    notification_data = {
        'notification': notification_tracker.notif_id,
        'user': user.id,
        'sent_time': sent_time,
        'open_time': open_time,
        'platform': platform,
        'notification_type': notification_type,
    }
    return notification_data


def track_notifications(data, user, platform):
    if platform is None:
        print('Cannot track notifications! Platform not defined!')
        return
    notification_tracker = NotificationTracker.objects.get(notif_id=data['notif_id'], user=user,
                                                           sent_time=parser.parse(data['sent_time']).replace(
                                                               tzinfo=None))
    notification_tracker.opened_time = parser.parse(data['opened_time'])
    notification_tracker.save()


# @task
# def initiate_campaign(start_time, campaign_id):
#     campaign = Campaign.objects.get(id=campaign_id)
#     for camp_time in campaign.campaign_time.all():
#         camp_time.is_running = True
#         camp_time.save()
#         if start_time == camp_time.start_datetime:
#             campaign_products = campaign.campaign_product.all()
#             for pro in campaign_products:
#                 pro.original_listing_price = pro.products.listing_price
#                 pro.save()
#                 pro.products.listing_price = int(
#                     round(pro.products.listing_price - (pro.discount / 100 * pro.products.listing_price)))
#                 pro.products.discount = ((pro.products.original_price - (
#                 pro.discount / 100 * pro.products.listing_price)) / pro.products.original_price)
#                 pro.products.save()


# @task
# def end_campaign(end_time, campaign_id):
#     campaign = Campaign.objects.get(id=campaign_id)
#     for camp_time in campaign.campaign_time.all():
#         camp_time.is_running = False
#         camp_time.has_ended = True
#         camp_time.save()
#         if end_time == camp_time.end_datetime:
#             campaign_products = campaign.campaign_product.all()
#             for pro in campaign_products:
#                 pro.products.listing_price = pro.original_listing_price
#                 pro.products.discount = (
#                 (pro.products.original_price - pro.original_listing_price) / pro.products.original_price)
#                 pro.products.save()


# @task
# def end_campaign_now(campaign_id):
#     campaign = Campaign.objects.get(id=campaign_id)
#     campaign_products = campaign.campaign_product.all()
#     for pro in campaign_products:
#         pro.products.listing_price = pro.original_listing_price
#         pro.products.discount = (
#         (pro.products.original_price - pro.original_listing_price) / pro.products.original_price)
#         pro.products.save()