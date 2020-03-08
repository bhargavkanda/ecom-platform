import pika
import json
import pdb
from django.conf import settings


def send_to_queue(data, reg_id_list, current_domain, logged_device):
    
    # pdb.set_trace()
    credentials = pika.PlainCredentials(
            'zapyle', 'zapy!e1234')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
      credentials=credentials,
      host='50.18.211.30',
      socket_timeout=300,
    ))
    print 'connected'
    channel = connection.channel()
    try:
      channel.queue_declare(queue=settings.BULK_NOTIFICTAION_QUEUE, durable=True)
    except:
      channel = connection.channel()

    data_req = {'data':data, 'reg_id_list':list(reg_id_list), 'current_domain':current_domain, 'logged_device':logged_device}
    channel.basic_publish(exchange='',
                          routing_key=settings.BULK_NOTIFICTAION_QUEUE,
                          body=json.dumps(data_req),
                  properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                ))
    print " [x] Sent"
    connection.close()
    return 'Completed'



