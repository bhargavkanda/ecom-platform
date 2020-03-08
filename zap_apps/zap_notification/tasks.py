from celery import task
from django.core.mail import EmailMessage, EmailMultiAlternatives
import requests
from pushbots import Pushbots
from django.conf import settings
from zap_apps.zap_notification.models import Notification
from zap_apps.zapuser.models import ZAPGCMDevice
import random
import pdb

def pushbotmsg(msg, alias, payload=None):

    pushbots = Pushbots(app_id=settings.PUSHBOT_ID,
                        secret=settings.PUSHBOT_SECRET)
    api_url = 'https://api.pushbots.com/push/all'
    headers = pushbots.headers
    if payload:
        data = {'platform': '0', 'msg': msg,
                'sound': 'default', 'badge': '1', 'alias': alias, 'payload': payload}
    else:    
        data = {'platform': '0', 'msg': msg,
                'sound': 'default', 'badge': '1', 'alias': alias}
    code, msg = pushbots.post(api_url=api_url, headers=headers, data=data)


@task
def func_runner(func, attributes=[]):
    if attributes:
        func(*attributes)
    else:
        func()


@task
def func_runner_2(func, attributes=[]):
    if attributes:
        func(*attributes)
    else:
        func()

@task
def email_task(subject, from_email, to_email, template_name, email_vars):
    msg = EmailMessage(
        subject=subject, from_email=from_email, to=to_email)
    # import pdb; ######pdb.set_trace()
    msg.template_name = template_name
    if email_vars:
        msg.global_merge_vars = email_vars
        
    msg.send()

@task
def email_task_attach(subject, from_email, to_email, email_body, template_id, email_vars, attachment,attachment_name):
    msg = EmailMessage(
        subject=subject, from_email=from_email, to=to_email)
    # import pdb; ######pdb.set_trace()
    if template_id:
        msg.template_id = template_id
    if email_body:
        msg.body = email_body

    if email_vars:
        msg.global_merge_vars = email_vars

    if attachment:
        attachment = open(attachment,'rb')
        msg.attach(attachment_name, attachment.read(), "application/pdf")
        
    msg.send()

@task
def email_alternative_task(subject, from_email, to_email, html_body, attachment, attachment_name):
    msg = EmailMultiAlternatives(subject=subject,
                                 from_email=from_email, to=to_email, body=html_body)

    
    # pdb.set_trace()
    if attachment_name:
        attachment = open(attachment,'rb')
        msg.attach(attachment_name, attachment.read(), "application/pdf")
    msg.attach_alternative(html_body, "text/html")
    # if settings.CELERY_USE:
    #     send_email_task(msg)
    # else:
    msg.send()


@task
def sms_task(full_nums, msg):
    for nums in full_nums:
        post_data = {
            "From": settings.EXOTEL_FROM,
            "To": nums,
            "Body": msg
        }
        r = requests.post(settings.EXOTEL_URL, post_data)
        print r.text


@task
def zaplogging(msg):
    with open(settings.BASE_DIR+'/zaplog.log','a') as f:
        f.write(msg+"\n")


@task
def gcm_task(users, msg, extra=None):
    from zap_apps.zap_notification.bulk_push_notif import send_to_queue
    if extra:
        extra['random_num'] = str(random.choice(range(100)))
    else:
        extra = {'random_num': str(random.choice(range(100)))}
    users = ZAPGCMDevice.objects.filter(id__in=users)
    users.send_message(msg, extra=extra)
    users = ZAPGCMDevice.objects.filter(id__in=users, active=True)
    # if len(users) > 1:

        # extra.update({"message":msg})
        # reg_id_list = users.values_list('registration_id', flat=True)

        # send_to_queue(extra, reg_id_list)

    users.send_message(msg, extra=extra)
        # ab = users.values_list('registration_id', flat=True)
        # print 'GCM '+str(len(users))
    # else:
    #     for i in users:
    #         i.send_message(msg, extra=extra)

            # print 'GCM loop 1'

@task
def gcm_multi_task(users, msg, extra=None):
    
    from zap_apps.zap_notification.bulk_push_notif import send_to_queue
    if extra:
        extra['random_num'] = str(random.choice(range(100)))
    else:
        extra = {'random_num': str(random.choice(range(100)))}
    android_users = ZAPGCMDevice.objects.filter(id__in=users, logged_device__name="android", active=True).exclude(user__zapuser__zap_username=None).distinct()
    ios_users = ZAPGCMDevice.objects.filter(id__in=users, logged_device__name="ios", active=True).exclude(user__zapuser__zap_username=None).distinct()
    # if len(users) > 1:

    extra.update({"message":msg})
    android_reg_id_list = android_users.values_list('registration_id', flat=True)
    ios_reg_id_list = ios_users.values_list('registration_id', flat=True)

    send_to_queue(extra, android_reg_id_list, settings.PUSH_NOTIF_DOMAIN, 'android')
    send_to_queue(extra, ios_reg_id_list, settings.PUSH_NOTIF_DOMAIN, 'ios')


@task
def pushbot_task(users, msg, payload=None):
    # #pdb.set_trace()
    users = ZAPGCMDevice.objects.filter(id__in=users).values_list('user__zapuser__zap_username', flat=True).exclude(user__zapuser__zap_username=None).distinct()
    print len(users)
    for i in users:
        pushbotmsg(msg.decode('unicode_escape'), i, payload=payload)
        # print 'pushbot loop 1'


@task
def mark_notifications_seen(notif_ids):
    for notif_id in notif_ids:
        notification = Notification.objects.get(id=notif_id)
        notification.seen = True
        notification.save()



def gcm_handle_canonical_id(canonical_id, current_id):

    """
    Handle situation when GCM server response contains canonical ID
    """
    if ZAPGCMDevice.objects.filter(registration_id=canonical_id, active=True).exists():
        ZAPGCMDevice.objects.filter(registration_id=current_id).update(active=False)
    else:
        ZAPGCMDevice.objects.filter(registration_id=current_id).update(registration_id=canonical_id)
    print 'Canonical ids removed'

@task
def remove_canonical_zapgcm_id(canonical_ids, ids_to_remove=None):
    if ids_to_remove:
        ZAPGCMDevice.objects.filter(registration_id__in=ids_to_remove).update(active=0)

    for old_id, new_id in canonical_ids:
            gcm_handle_canonical_id(new_id, old_id)

    return {'canonical':canonical_ids, 'deleted':ids_to_remove}