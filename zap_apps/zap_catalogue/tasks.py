from celery import task
import requests
from django.conf import settings
import json
import re

from zap_apps.zap_analytics.analytics_serializers import ImpressionAnalyticsSerializer
from zap_apps.zapuser.models import ZapUser
from zap_apps.zap_notification.views import ZapEmail, PushNotification, ZapSms
from zap_apps.zap_notification.models import Notification
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from cStringIO import StringIO
import os
from zap_apps.zap_catalogue.models import *

# import pdb
# Tasks defined here


@task
def send_to_tornado(p_id, u_id):
    from zap_apps.zap_catalogue.models import ApprovedProduct
    from zap_apps.zap_catalogue.product_serializer import ApprovedProductSerializerAndroid
    p = ApprovedProduct.ap_objects.filter(id=p_id)
    u = ZapUser.objects.get(id=u_id)
    srlzr = ApprovedProductSerializerAndroid(p, many=True,
                                             context={'logged_user': u})
    data = srlzr.data[0]
    data['sold_out'] = False
    data['available'] = True
    requests.post(url=settings.TORNADO_URL, data=json.dumps(data))



@task
def after_comment_post(comment_id):
    from zap_apps.zap_catalogue.product_serializer import ConversationsSerializer
    from zap_apps.zap_catalogue.models import Comments
    pushnots = PushNotification()
    result = {}
    try:
        # print str(comment_id) + "----------------------"
        comment_obj = Comments.objects.get(id=comment_id)

        users_list = re.findall(r'[@]\w+', comment_obj.comment)
        username_list = [i[1:] for i in users_list]

        mentioned_user_obj_list = ZapUser.objects.filter(zap_username__in=username_list)
        if mentioned_user_obj_list:
            srlzr = ConversationsSerializer(data={'comment':comment_obj.id,'mentions':mentioned_user_obj_list})
            if srlzr.is_valid():
                srlzr.save()
            mention_msg = str(comment_obj.commented_by.zap_username or comment_obj.commented_by.get_full_name()) + " mentioned you on a comment."
            for user in mentioned_user_obj_list:
                Notification.objects.create(user=user, product=comment_obj.product,
                                    notified_by=comment_obj.commented_by, message=mention_msg, action="co")
            # extra_data = {
            #     'action':'notif',
            #     # 'profile_id':user.id,
            #     # 'profile_name':user.zap_username,
            #     # 'profile_type':user.user_type.name,
            #     # 'profile_pic':user.user.profile_pic,
            #     'marketing':False,
            #     'notif_id': str(notif['id']),
            #     'sent_time': sent_time
            # }

            pushnots.send_notification(mentioned_user_obj_list, mention_msg)



        product_user_msg = str(comment_obj.commented_by.zap_username or comment_obj.commented_by.get_full_name()) + \
            " commented on your product - " + \
            str(comment_obj.product.title or "")
        other_users_msg = str(comment_obj.commented_by.zap_username or comment_obj.commented_by.get_full_name()) + " commented on the product - " + str(comment_obj.product.title or "")

        other_user_id_list = comment_obj.product.comments_got.exclude(commented_by=comment_obj.commented_by).values_list('commented_by',flat=True)
        mentioned_user_id_list = mentioned_user_obj_list.values_list('id',flat=True)
        result.update({'mentioned_user':mentioned_user_id_list})


        if comment_obj.commented_by.id == comment_obj.product.user.id:
            other_users_list = ZapUser.objects.filter(id__in=other_user_id_list).exclude(id__in=mentioned_user_id_list)
            result.update({'product':[]})
            # for user in other_users_list:
            #     Notification.objects.create(user=user, product=comment_obj.product, notified_by=comment_obj.commented_by, message=other_users_msg, action="co")
            # pushnots.send_notification(other_users_list, other_users_msg)

        else:
            exclude_users = list(mentioned_user_id_list) + [comment_obj.product.user.id]
            other_users_list = ZapUser.objects.filter(id__in=other_user_id_list).exclude(id__in=exclude_users)
            if comment_obj.product.user.id not in mentioned_user_id_list:
                Notification.objects.create(user=comment_obj.product.user, product=comment_obj.product, notified_by=comment_obj.commented_by, message=product_user_msg, action="co")
                pushnots.send_notification(comment_obj.product.user, product_user_msg)
                result.update({'product_user':[comment_obj.product.user.id]})




        if other_users_list:   
            for user in other_users_list:
                Notification.objects.create(user=user, product=comment_obj.product, notified_by=comment_obj.commented_by, message=other_users_msg, action="co")
            pushnots.send_notification(other_users_list, other_users_msg)    
            result.update({'other_user':other_users_list.values_list('id', flat=True)})


        
        # pushnots.send_notification(instance.product.user, msg)
        # Notification.objects.create(user=instance.product.user, product=instance.product,
        #                             notified_by=instance.commented_by, message=msg, action="co")
        # import pdb; pdb.set_trace()
        return result

    except Exception as e:
        print e



@task
def after_love_notif(love_id):
    from zap_apps.zap_catalogue.models import Loves
    pushnots = PushNotification()
    try:
        love_obj = Loves.objects.get(id=love_id)
        msg = str(love_obj.loved_by.zap_username or love_obj.loved_by.get_full_name()) + \
            " loved your product - " + (love_obj.product.title or "")
        Notification.objects.create(user=love_obj.product.user, product=love_obj.product,
                                    notified_by=love_obj.loved_by, message=msg, action="lo")
        pushnots.send_notification(love_obj.product.user, msg)

    except:
        print "No object found!"


@task
def product_view_tracker(user_id,product_id):
    if settings.MONGO_DB_TRACKER:
        from zap_apps.zap_catalogue.models import ProductViewTracker
        if not isinstance(user_id,str):
            user_id = str(user_id)
        track = ProductViewTracker.objects(user=user_id).modify(upsert=True,new=True,set__user=user_id)
        track.modify(push__products={'id':product_id, 'time':str(timezone.now())})
        track.save()



@task
def image_compression(f, name, q, size=None):
    print locals()
    image = Image.open(f)
    if size:
        image.thumbnail(size, Image.ANTIALIAS)
    image.save(name, quality=q, optimize=True)


# Updates the score of products every 24 hours
@periodic_task(run_every=(crontab(minute=0, hour=0)))
def update_product_score():
    from zap_apps.zap_catalogue.models import ApprovedProduct
    product_objects = ApprovedProduct.objects.all()
    for product in product_objects:
        product.score = product.score - 1
        product.save()

@task
def send_to_elasticsearch(p):
    from zap_apps.zap_catalogue.models import ApprovedProduct
    from zap_apps.zap_admin.admin_serializer import ElasticProductsSerializer
    data = ''
    # p = ApprovedProduct.objects.get(id=product_id)
    if p.status == '1':
        if p.sale == '2':
            data += '{"index": {"_id": "%s"}}\n' % p.id
            data += json.dumps(ElasticProductsSerializer(p).data) + '\n'
            response = requests.put(url=settings.ELASTIC_URL+'_bulk', data=data)
        else:
            response = requests.delete(settings.ELASTIC_URL+str(p.id))    
    else:
        response = requests.delete(settings.ELASTIC_URL+str(p.id))
