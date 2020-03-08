import pika
import requests
import json
#import pdb
import sys,os
# sys.path.append("/path/to/project")
import django
try:
    env = sys.argv[1]
except IndexError:
    raise Exception("Please provide settings [local/ staging/ prod]")

os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.{}".format(env)
django.setup()
from django.conf import settings
# from zap_apps.zapuser.models import ZAPGCMDevice
from zap_apps.zap_notification.tasks import remove_canonical_zapgcm_id
credentials = pika.PlainCredentials(
        'zapyle_push', 'zapy!e1234')
connection = pika.BlockingConnection(pika.ConnectionParameters(
  credentials=credentials,
  host='localhost',
  # socket_timeout=300,
))
channel = connection.channel()
try:
    channel.queue_declare(queue=settings.BULK_NOTIFICTAION_RESP_QUEUE, durable=True)
except:
    channel = connection.channel()

# def _gcm_send(data, content_type):
#  #   pdb.set_trace()
#    # data = json.dumps(data)
#     key = GCM_API_KEY
#     if not key:
#         raise ImproperlyConfigured('You need to set GCM_API_KEY to send messages')

#     headers = {
#         "Content-Type": content_type,
#         "Authorization": "key=%s" % (key),
#         "Content-Length": str(len(data)),
#     }

#     resp = requests.post(GCM_POST_URL, data=data, headers=headers)
#     json_response = resp.json()
#     return json_response
# def _chunks(l, n):
#     """
#     Yield successive chunks from list \a l with a minimum size \a n
#     """
#     for i in range(0, len(l), n):
#         yield l[i:i + n]
# def _gcm_handle_canonical_id(canonical_id, current_id):

#     """
#     Handle situation when GCM server response contains canonical ID
#     """
#     if ZAPGCMDevice.objects.filter(registration_id=canonical_id, active=True).exists():
#         ZAPGCMDevice.objects.filter(registration_id=current_id).update(active=False)
#     else:
#         ZAPGCMDevice.objects.filter(registration_id=current_id).update(registration_id=canonical_id)
#     print 'Canonical ids removed'


def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)

    data_req = json.loads(body)
    remove_canonical_zapgcm_id.apply_async(args=[data_req['canonical_ids'],data_req['ids_to_remove']], countdown=900)

    # if data_req['ids_to_remove']:
    #     ZAPGCMDevice.objects.filter(registration_id__in=data_req['ids_to_remove']).update(active=0)

    # for old_id, new_id in data_req['canonical_ids']:
    #         _gcm_handle_canonical_id(new_id, old_id)

    # print " [x] Done"
    # ch.basic_publish(exchange='',
    #                  routing_key=properties.reply_to,
    #                  body=str("ookkk"),
    #                  properties=pika.BasicProperties(
    #                     delivery_mode = 2, # make me$
    #                     reply_to = 'reply_hello2',
    #                  )          
    # )
    # ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=settings.BULK_NOTIFICTAION_RESP_QUEUE,no_ack=True)
print ' [*] Waiting for messages. To exit press CTRL+C'

channel.start_consuming()