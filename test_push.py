import pika
import requests
import json
#import pdb

credentials = pika.PlainCredentials(
        'zapyle', 'zapy!e1234')
connection = pika.BlockingConnection(pika.ConnectionParameters(
  credentials=credentials,
  host='localhost',
  socket_timeout=300,
))
channel = connection.channel()
try:
    channel.queue_declare(queue='test_push_queue', durable=True)
except:
    channel = connection.channel()
GCM_API_KEY = (
    ('android','AIzaSyDVvrcs1ezmWRX_jiaz5flXwIHoos3lOn8'),
    ('ios','AIzaSyC-LtlJDqDIOCJuqRGrs5JhAXmnNH6asZc')
    )

GCM_POST_URL = 'https://android.googleapis.com/gcm/send'
MAX_CHUNK_LENGTH = 1000

def _gcm_send(data, content_type, logged_device):
 #   pdb.set_trace()
   # data = json.dumps(data)
    key = dict(GCM_API_KEY).get(logged_device)
    if not key:
        raise ImproperlyConfigured('You need to set GCM_API_KEY to send messages')

    headers = {
        "Content-Type": content_type,
        "Authorization": "key=%s" % (key),
        "Content-Length": str(len(data)),
    }

    resp = requests.post(GCM_POST_URL, data=data, headers=headers)
    json_response = resp.json()
    return json_response
def _chunks(l, n):
    """
    Yield successive chunks from list \a l with a minimum size \a n
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]

def send_response_to_queue(data, current_domain):
  #  pdb.set_trace()
    resp_credentials = pika.PlainCredentials(
            'zapyle_push', 'zapy!e1234')
    resp_connection = pika.BlockingConnection(pika.ConnectionParameters(
      credentials=resp_credentials,
      host=current_domain,
      socket_timeout=300,
    ))
    print 'connected'
    resp_channel = resp_connection.channel()
    try:
      resp_channel.queue_declare(queue='test_push_response_queue', durable=True)
    except:
      resp_channel = connection.channel()

    # data_req = {'data':data, 'reg_id_list':list(reg_id_list)}
    resp_channel.basic_publish(exchange='',
                          routing_key='test_push_response_queue',
                          body=json.dumps(data),
                  properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                ))
    print " [x]Response Sent"
    resp_connection.close()
    return 'Response Chunk Completed'

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)

    data_req = json.loads(body)

    for chunk in _chunks(data_req['reg_id_list'], MAX_CHUNK_LENGTH):
        response_to_queue_dict = {}
        if data_req['logged_device'] == "android":
            response = _gcm_send(json.dumps({'registration_ids':chunk,
                'data':{'sound':'default', 'badge':'1','title':'Zapyle',
                'body':data_req['data']}, 'priority':'high', 'content_available':True}), 'application/json', data_req['logged_device'])
        else:
            response = _gcm_send(json.dumps({'data':data_req['data'], 'registration_ids':chunk,
                'notification':{'sound':'default', 'badge':'1','title':'Zapyle',
                'body':data_req['data']['message']}, 'priority':'high', 'content_available':True}), 'application/json', data_req['logged_device'])
        print response
        #pdb.set_trace()
        if 'localhost' not in data_req['current_domain']:
            if response["failure"] or response["canonical_ids"]:
                ids_to_remove, old_new_ids = [], []
                # throw_error = False
                for index, result in enumerate(response["results"]):
                    error = result.get("error")
                    if error:
                        # Information from Google docs (https://developers.google.com/cloud-messaging/http)
                        # If error is NotRegistered or InvalidRegistration, then we will deactivate devices because this
                        # registration ID is no more valid and can't be used to send messages, otherwise raise error
                        if error in ("NotRegistered", "InvalidRegistration"):
                            ids_to_remove.append(chunk[index])

                    # If registration_id is set, replace the original ID with the new value (canonical ID) in your
                    # server database. Note that the original ID is not part of the result, so you need to obtain it
                    # from the list of registration_ids passed in the request (using the same index).
                    new_id = result.get("registration_id")
                    if new_id:
                        old_new_ids.append((chunk[index], new_id))
                response_to_queue_dict = {'ids_to_remove':ids_to_remove, 'canonical_ids':old_new_ids}
                send_response_to_queue(response_to_queue_dict, data_req['current_domain'])

    print " [x] Done"

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='test_push_queue',no_ack=True)
print ' [*] Waiting for messages. To exit press CTRL+C'

channel.start_consuming()
