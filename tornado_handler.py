import sys,os
# sys.path.append("/path/to/project")
import django
try:
    env = sys.argv[1]
except IndexError:
    raise Exception("Please provide settings [local/ staging/ prod]")

try:
    env_port = sys.argv[2]
except IndexError:
    raise Exception("Please provide port")

os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.{}".format(env)
django.setup()
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import tornado.httpserver
import urllib
import requests
import threading
from tornado.wsgi import WSGIContainer
import tornado.wsgi
from zap_apps.zap_catalogue.models import Comments,ApprovedProduct
from zap_apps.zapuser.models import ZapUser
from zap_apps.zapuser.zapuser_serializer import MentionSerializer
from django.db.models import Q
from itertools import chain
from tornado.ioloop import PeriodicCallback
# import pdb

# print Comments.objects.all()


clients = []
mention_clients = []
class MainHandler(tornado.web.RequestHandler):
    def post(self):
        EchoWebSocket(self.application, self.request).broadcast_msg(self.request.body)

class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        print ">>>>>>>>>>>>>>>>>>>"
        return True
        # parsed_origin = urllib.parse.urlparse(origin)
        # if any(i in parsed_origin.netloc for i in ['zapyle.com', 'localhost']):
        #     return True
        # return False
    def sms_task(self, ww):
        requests.get("http://bhashsms.com/api/sendmsg.php?user=Zapyle&pass=zapyle@123&sender=ZAPYLE&phone={}&text={}&priority=ndnd&stype=normal".format(9895685141, "Test: Yeah tornado is working"))
    def open(self):
        clients.append(self)
        self.callback = PeriodicCallback(self.send_hello, 1000*50)
        self.callback.start()
        print("WebSocket opened")
    def send_hello(self):
        print ">>>>"
        
        self.write_message('no msg')
    def broadcast_msg(self, msg):
        # t = threading.Thread(target=self.sms_task, args=('dddd',))
        # t.start()
        for i in clients:
            print "sending"
            i.write_message(msg)

    def on_close(self):
        clients.remove(self)
        self.callback.stop()
        print("WebSocket closed")

class MentionWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        print origin
        return True

    def open(self):
        # clients.append(self)
        print("WebSocket opened")


    def on_message(self,msg):

        # 
        # print msg
        try:
            print msg
            msg = json.loads(msg)
            print msg
            # ##pdb.set_trace()
            if msg['request_type'] == 'post':
                Q1 = Q(zap_username__istartswith=msg['name'])
                Q2 = Q(first_name__istartswith=msg['name'])
                Q3 = Q(last_name__istartswith=msg['name'])
                ex_Q1 = Q(zap_username__isnull=True)
                ex_Q2 = Q(zap_username="")
                ex_Q3 = Q(id=msg['user_id'])

                product = ApprovedProduct.ap_objects.get(id=msg['product_id'])
                current_user = ZapUser.objects.get(id = msg['user_id'])


                commented_users = product.comments_got.all().values_list('id',flat=True)
                admiring_users = current_user.aaaa.all().values_list('id',flat=True)
                admirers_users = current_user.profile.admiring.all().values_list('id',flat=True)

                sort_ids = list(chain(commented_users,admirers_users,admirers_users))

                Q4 = Q(id__in=sort_ids)

                ordered_users = ZapUser.objects.filter(Q4 & (Q1 | Q2 | Q3)).exclude(ex_Q1 | ex_Q3 | ex_Q3)
                exclude_users_list = list(sort_ids)+[msg['user_id']]
                ex_Q4 = Q(id__in=exclude_users_list)

                remaining_users = ZapUser.objects.filter(Q1 | Q2 | Q3).exclude(ex_Q1 | ex_Q2 | ex_Q4)
                suggested_users = list(chain(ordered_users,remaining_users))[:30]

                srlzr = MentionSerializer(suggested_users, many=True)
                if srlzr.data:
                    self.write_message(json.dumps({'data':srlzr.data}))
                else:
                    self.write_message("no msg")
            else:
                user = ZapUser.objects.get(zap_username=msg['username'])
                resp = {'user_id':user.id}
                self.write_message(json.dumps(resp))

        except Exception as e:
            print e
            self.write_message("no msg")
        # self.write_message(json.dumps(msg))
        # print "agcvsavcs"
    def on_close(self):
        # clients.remove(self)
        print("WebSocket closed")

# class CommentWebSocket(tornado.websocket.WebSocketHandler):

#     def check_origin(self, origin):
#         print origin
#         return True

#     # def open(self):


#     def on_message(self,msg):
#         try:
#             msg = json.loads(msg)
#             user = ZapUser.objects.get(zap_username=msg['username'])
#             resp = {'user_id':user.id,"no_user":False}
#             self.write_message(json.dumps(resp))
#         except:
#             self.write_message(json.dumps({"no_user":True}))








# if __name__ == "__main__":
#     main()
def make_app():
    return tornado.web.Application([
        (r"/odanrot", MainHandler),
        (r"/sock", EchoWebSocket),
        (r"/mention",MentionWebSocket),
        # (r"/comment",CommentWebSocket),
    ])

# app = make_app()
# # server = tornado.httpserver.HTTPServer(app)
# # server.bind(8888)
# # tornado.ioloop.IOLoop.current().start()
# http_server = tornado.httpserver.HTTPServer(app)
# http_server.listen(8888)
# tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    app = make_app()
    app.listen(env_port)
    tornado.ioloop.IOLoop.current().start()
#tornado_app = make_app()
#application = tornado.wsgi.WSGIAdapter(tornado_app)

# tornado_app = make_app()
# application = tornado.wsgi.WSGIAdapter(tornado_app)
