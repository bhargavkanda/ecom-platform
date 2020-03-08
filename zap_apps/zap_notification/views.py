import ast

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.utils import timesince

from zap_apps.account.zapauth import ZapView, ZapAuthView
from zap_apps.zap_notification.models import Notification
from zap_apps.zap_notification.tasks import *
from zap_apps.zapuser.models import ZAPGCMDevice
from zap_apps.zapuser.models import ZapUser
from zapyle_new.settings.subscribers_emails import subscriber_email


# Create your views here.


class GetMyNotifs(ZapAuthView):

    def get(self, request, page=None, format=None):
        notifications = Notification.objects.filter(user=request.user)
        if settings.CELERY_USE:
            mark_notifications_seen.delay([notification.id for notification in notifications])
        else:
            mark_notifications_seen([notification.id for notification in notifications])
        notification_data = [{
            'id':i.id,
            'notified_by': {'id': i.notified_by.id, 'name': i.notified_by.zap_username, 'profile_img_url': i.notified_by.profile.profile_pic or "", 'user_type': i.notified_by.user_type.name} if i.notified_by else {},
            'product': {'id': i.product.id, 'name': i.product.title, 'img_url': i.product.images.all()[0].image.url_100x100} if i.product else {},
            'message': i.message,
            'action': i.get_action_display(),
            'notif_time': timesince.timesince(i.notif_time) + " ago.",
        } for i in notifications]

        if not page:
            return self.send_response(1, notification_data)

        perpage = request.GET.get('perpage', settings.NOTIFICATION_PERPAGE)
        paginator = Paginator(notification_data, perpage)
        if page:
            page = int(page)
        if not paginator.num_pages >= page or page == 0:
            data = {
                'data': [],
                'page': page,
                'total_pages': paginator.num_pages,
                'next': True if page == 0 else False,
                'previous': False if page == 0 else True}
            return self.send_response(1, data)
        p = paginator.page(page)
        data = {'data': notification_data, 'page': page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}
        return self.send_response(1, data)


    def delete(self, request, format=None):
        data = request.GET.copy()
        if not 'notif_id' in data:
            return self.send_response(0, "\'notif_id\' field is required")
        Notification.objects.filter(id=data['notif_id']).delete()
        return self.send_response(1, "Successfully deleted.")


class PushNotification(object):

    def __init__(self):
        pass
        #self.emails = ZapUser.objects.all().values('email')

    # Send push notifications
    def send_notification(self, user, msg, extra=None):
        if settings.PUSH_NOTIFICATION_ENABLE:
            if not (isinstance(user, list) or isinstance(user,QuerySet)):
                user = [user]
            if settings.CELERY_USE:

                gcm_multi_task.delay([i.id for i in ZAPGCMDevice.objects.filter(user__zapuser__in=user).distinct('user')], msg, extra=extra)
            else:
                gcm_multi_task([i.id for i in ZAPGCMDevice.objects.filter(user__zapuser__in=user)], msg, extra=extra)
                

    # def marketing_bulk_notification(self, msg, extra=None):
    #     if settings.PUSH_NOTIFICATION_ENABLE:
    #         if settings.CELERY_USE:
    #             gcm_multi_task.delay([i.id for i in ZAPGCMDevice.objects.filter(logged_device__name="android")], msg, extra=extra)
    #         else:
    #             gcm_multi_task(ZAPGCMDevice.objects.filter(logged_device__name="android"), msg, extra=extra)
    #         # if settings.CELERY_USE:
    #         #     pushbot_task.delay([i.id for i in ZAPGCMDevice.objects.filter(logged_device__name="ios")], msg, payload=extra)
    #         # else:
    #         #     pushbot_task(ZAPGCMDevice.objects.filter(logged_device__name="ios"), msg, payload=extra)


class ZapEmail(object):

    def __init__(self):
        pass
        #self.emails = ZapUser.objects.all().values('email')

    def send_bulk_email(self, template_name, subject, email_vars, from_email, email_group):
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if email_group == 'AllUsers':
                full_emails = [i['email']
                           for i in ZapUser.objects.all().values('email') if i['email'] ]
            elif email_group == 'RawValue':
                full_emails = ast.literal_eval(data_recieved['raw_users'])

            elif email_group == 'RegisteredAndSubscriber':
                full_emails = [i['email']
                           for i in ZapUser.objects.all().values('email') if i['email'] ]
                full_emails += subscriber_email
                all_emails = map(lambda x:x.lower(),full_emails)

                full_emails = list(set(all_emails))
            if settings.CELERY_USE:
                email_task.delay(subject, from_email, full_emails, template_name, email_vars)
            else:
                email_task(subject, from_email, full_emails, template_name, email_vars)

    def send_email(self, template_name, subject, email_vars, from_email, to_email):
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if not isinstance(to_email, list):
                to_email = [to_email]
            msg = EmailMessage(
                subject=subject, from_email=from_email, to=to_email)
            # import pdb; #######pdb.set_trace()
            
            if template_name:
                msg.template_name = template_name

            if email_vars:
                msg.global_merge_vars = email_vars
            # msg.send()
            # import pdb; ######pdb.set_trace()

            # msg.send()

            if settings.CELERY_USE:
                email_task.delay(subject, from_email, to_email, template_name, email_vars)
            else:
                email_task(subject, from_email, to_email, template_name, email_vars)

    def send_email_attachment(self, subject, from_email, to_email,email_body=None, template_id=None, email_vars=None, attachment=None, attachment_name=None):
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if not isinstance(to_email, list):
                to_email = [to_email]
            

            if settings.CELERY_USE:
                email_task_attach.delay(subject, from_email, to_email, email_body, template_id, email_vars, attachment, attachment_name)
            else:
                email_task_attach(subject, from_email, to_email, email_body, template_id, email_vars, attachment, attachment_name)

    def send_email_alternative(self, subject, from_email, to_email, html_body, attachment=None, attachment_name=None):
        if settings.EMAIL_NOTIFICATION_ENABLE:
        # pdb.set_trace()
            if not isinstance(to_email, list):
                to_email = [to_email]
            if settings.CELERY_USE:
                email_alternative_task.delay(subject, from_email, to_email, html_body, attachment, attachment_name)
            else:
                email_alternative_task(subject, from_email, to_email, html_body, attachment, attachment_name)

    def send_email_plus_msg(self, text, template_name, subject, email_vars, from_email, to_email):
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if not isinstance(to_email, list):
                to_email = [to_email]
            msg = EmailMessage(
                subject=subject, from_email=from_email, to=to_email)
            # import pdb; #######pdb.set_trace()
            if text:
                msg.body = text
            
            if template_name:
                msg.template_name = template_name
            
            if email_vars:
                msg.global_merge_vars = email_vars
            # msg.send()
            # import pdb; ######pdb.set_trace()
            if settings.CELERY_USE:
                func_runner.delay(msg.send)
            else:
                email_task(subject, from_email, to_email, template_name, email_vars)


class ZapSms(object):

    def __init__(self):
        pass
        # self.url = "http://bhashsms.com/api/sendmsg.php?user=Zapyle&pass=zapyle@123&sender=ZAPYLE&phone={}&text={}&priority=ndnd&stype=normal"

    def send_bulk_sms(self, msg):
        if settings.SMS_NOTIFICATION_ENABLE:
            full_nums = filter(
                None, [(i.phone_number[-10:]).encode('UTF8') for i in ZapUser.objects.all() if hasattr(i, 'phone_number') and i.phone_number])
            if settings.CELERY_USE:
                sms_task.delay(full_nums, msg)
            else:
                sms_task(full_nums, msg)
                # requests.get(self.url.format(str(i)[-10:], msg))

    def send_sms(self, phone_number, msg, action=None):
        if action == 'forgot' or settings.SMS_NOTIFICATION_ENABLE:
            if not isinstance(phone_number, list):
                phone_number = [phone_number]

            if settings.CELERY_USE:
                sms_task.delay(phone_number, msg)
            else:
                import threading
                t = threading.Thread(target=sms_task, args=(phone_number, msg,))
                t.start()


from rest_framework.response import Response
from rest_framework.decorators import api_view
from zap_apps.account.zapauth import admin_only


@api_view(['GET', 'POST', ])
@admin_only
def SendSMS(request):
    print request.data
    data_recieved = request.data
    users = data_recieved['users']
    message = data_recieved['message']
    types = data_recieved['type']
    sms = ZapSms()
    if types == 'AllUsers':
        sms.send_bulk_sms(message)
    else:
        full_nums = filter(None, [i.phone_number for i in ZapUser.objects.filter(
            id__in=users) if hasattr(i, 'phone_number')])
        print full_nums, 'full_nums'
        sms.send_sms(full_nums, message)
    return Response({'status': 'success'})


@api_view(['GET', 'POST', ])
@admin_only
def SendEMAIL(request):
    print request.data['data'],'-------------'
    return Response({'status': 'error'})
    zapemail = ZapEmail()
    data_recieved = request.data['data']
    text = data_recieved.get('message', '')
    template_name = data_recieved.get('template','')

    if data_recieved['type'] == 'selectedUsers':
        print 'selected'
        full_emails = filter(None, [i.email for i in ZapUser.objects.filter(
            id__in=data_recieved['users']) if hasattr(i, 'email')])
        print full_emails, ' full_emails'

        # import pdb; ######pdb.set_trace()
        if text:
            zapemail.send_email_plus_msg(text,template_name, data_recieved[
                            'subject'], '', data_recieved['from'], full_emails)
            return Response({'status': 'success'})

        zapemail.send_email(template_name, data_recieved[
                            'subject'], '', data_recieved['from'], full_emails)

    else:
        zapemail.send_bulk_email(data_recieved['template'], data_recieved[
                            'subject'], '', data_recieved['from'], data_recieved['type'])

    # if data_recieved['type'] == :
        
    
        
        
    return Response({'status': 'success'})


@api_view(['GET', 'POST', ])
@admin_only
def SendPushData(request):
    from zap_apps.zap_catalogue.models import ApprovedProduct
    data_recieved = request.data['data']
    print data_recieved,'***'
    if data_recieved['marketing_action'] == 'product':
        product = ApprovedProduct.objects.get(id=data_recieved['target_id'])
        data = {
            'action':'product',
            'product_id':product.id,
            'product_title':product.title,
            'product_img_url':product.images.all()[0].image.url_100x100,
            'product_sale':product.get_sale_display()
        }
        print data
    elif data_recieved['marketing_action'] == 'profile':
        profile = ZapUser.objects.get(id=data_recieved['target_id'])
        data = {
            'action':'profile',
            'profile_id':profile.id,
            'profile_name':profile.zap_username,
            'profile_type':profile.user_type.name,
            'profile_pic':profile.profile.profile_pic
        }
        print data
    elif data_recieved['marketing_action'] == 'newsfeed':
        data = {
            'action':'newsfeed'
        }
        print data
    elif data_recieved['marketing_action'] == 'zapexclusivecloset':
        profile = ZapUser.objects.get(user_type__name='zap_exclusive')
        data = {
            'action':'profile',
            'profile_id':profile.id,
            'profile_name':profile.zap_username,
            'profile_type':profile.user_type.name,
            'profile_pic':profile.profile.profile_pic
        }
        print data
    elif data_recieved['marketing_action'] == 'upload':
        data = {
            'action':'upload'
        }
        print data
    data['marketing'] = True
    p = PushNotification()
    data = {k:str(v) for k,v in data.items()}
    if data_recieved['type'] == 'AllUsers':
        p.send_notification(data_recieved['message'],extra=data)
    else:
        p.send_notification(data_recieved['users'],data_recieved['message'],extra=data)    
    return Response({'status': 'success'})


class ReadNotification(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        notif_id = data['notif_id']
        notification = Notification.objects.get(id=notif_id)
        notification.seen = True
        notification.read = True
        notification.save()
        return self.send_response(1, 'success')

from django.utils import timesince, timezone
import json
import urllib2

def get_json_for_push_notification(notif):
    sent_time = timezone.now()
    data = {}
    if notif.action.action_type == 'filtered':
        data = {
            'action_type': 'filtered',
            'target': '?'+notif.action.get_args_string(),

            'action': 'filtered',
            'args': notif.action.get_args_string(),
            "default_sound": True,
        }
    elif notif.action.action_type == 'product':
        from zap_apps.zap_catalogue.models import ApprovedProduct
        product = ApprovedProduct.ap_objects.get(id=notif.action.data['id'])
        data = {
            'action_type': 'product',
            'target': product.id,

            'action': 'product',
            'product_id': product.id,
            'product_title': product.title,
            'product_img_url': product.images.all()[0].image.url_100x100,
            'product_sale': product.get_sale_display(),
            "badge_count": 1,
        }
    elif notif.action.action_type == 'profile':
        profile = ZapUser.objects.get(id=notif.action.data['id'])
        data = {
            'action_type': 'profile',
            'target': profile.id,

            'action': 'profile',
            'profile_id': profile.id,
            'profile_name': profile.zap_username,
            'profile_type': profile.user_type.name,
            'profile_pic': profile.profile.profile_pic,
            "badge_count": 1,
        }
    elif notif.action.action_type == 'newsfeed':
        data = {
            'action_type': 'newsfeed',
            'target' : '',

            'action': 'newsfeed',
            "badge_count": 1,
        }
    elif notif.action.action_type == 'upload':
        data = {
            'action_type': 'upload',
            'target': '',

            'action': 'upload',
            "badge_count": 1,
        }
    elif notif.action.action_type == 'earn_cash':
        data = {
            'action_type': 'earn_cash',
            'target': '',

            'action': 'earn_cash',
            "badge_count": 1,
        }
    elif notif.action.action_type == 'update_app':
        data = {
            'action_type': 'update_app',
            'target': '',

            'action': 'update_app',
            "badge_count": 1,
        }
    elif notif.action.action_type == 'deep_link':
        data = {
            'action_type': 'deep_link',
            'target': '',

            'action' : 'deep_link',
            'target' : 'http://go.zapyle.com/WxOl/XlqVQE3gAy',
            "badge_count": 1,
        }
    data['marketing'] = True
    if notif.image:
        data['image'] = settings.CURRENT_DOMAIN + notif.image.url
    data['notif_id'] = str(notif.id)
    data['sent_time'] = str(sent_time)

    data = {k: str(v) for k, v in data.items()}
    return data

def clevertap_push_notification(json_data, data, notif):
    # pdb.set_trace()
    headers = {
        'X-CleverTap-Account-Id':'TEST-566-K95-464Z',
        'X-CleverTap-Passcode':'YMC-RUZ-AEAL',
        'Content-Type':' application/json'
    }
    clevertap_url='https://api.clevertap.com/1/send/push.json'

    if data['type'] == 'AllUsers':
        users = ZapUser.objects.values_list('id', flat=True)
    elif data['type'] == 'zapyleTeam':
        users = ZapUser.objects.filter(email__in=['shafi374@gmail.com','bhargavkanda@gmail.com','sundeepreddy10@gmail.com','sk@gmail.com','Rashigulati003@gmail.com','rashi@zapyle.com','haseeb@zapyle.com','rajeesh@gmail.com','likhita.nimmagadda@gmail.com','freda.pinto.gaia@gmail.com','m.ruby92@gmail.com']).values_list('id', flat=True)
    elif data['type'] == 'iosUsers':
        users = ZapUser.objects.filter(logged_device__name="ios").values_list('id', flat=True)
    elif data['type'] == 'androidUsers':
        users = ZapUser.objects.filter(logged_device__name="android").values_list('id', flat=True)
    else:
        u = ast.literal_eval(data['users'])
        if type(u) == tuple:
            data['users'] = list(u)  #unicode to list
        users = ZapUser.objects.filter(id__in=data['users']).values_list('id', flat=True)
    users_ids = [str(x) for x in users]
    if data['action_type'] == 'own_profile':
        for user in ZapUser.objects.filter(id__in=data['users']):
            sent_time = timezone.now()
            js_data = {
                'action_type': 'profile',
                'target': user.id,

                'action': 'profile',
                'profile_id': user.id,
                'profile_name': user.zap_username,
                'profile_type': user.user_type.name,
                'profile_pic': user.profile.profile_pic,
                'marketing': True,
                'notif_id': str(notif.id),
                'sent_time': str(sent_time),
                "badge_count": 1,
                'image': settings.CURRENT_DOMAIN + notif.image.url if notif.image else None
            }
            json_data = {k: str(v) for k, v in js_data.items()}
            # own_profile_list.append({'zap_username': user.zap_username, 'text': notif.text, 'data': data})
            b = {
                "to":{
                    "Identity":user.id
                    },
                "content":{
                    "title":data.get('title',''),
                    "body":data['text'],
                    "platform_specific":{
                        "android":json_data,
                        "ios":json_data
                    }
                }
            }
            bb = json.dumps(b)
            # print bb,'bb'
            req = urllib2.Request(clevertap_url, bb, headers)
            f = urllib2.urlopen(req)
            print f.read()
        return 'success'
    else:
        b = {
            "to":{
                "Identity":users_ids
                },
            "content":{
                "title":data.get('title',''),
                "body":data['text'],
                "platform_specific":{
                    "android":json_data,
                    "ios":json_data
                }
            }
        }
        bb = json.dumps(b)
        # print bb,'bb'
        req = urllib2.Request(clevertap_url, bb, headers)
        f = urllib2.urlopen(req)
        return f.read()
