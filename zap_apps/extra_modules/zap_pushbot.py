from django.conf import settings
import requests, json
from zap_apps.extra_modules.tasks import del_pushbot_token

class ZapPushbot:

    def __init__(self):
        self.app_id = settings.PUSHBOT_ID
        self.app_secret = settings.PUSHBOT_SECRET
        self.headers = {'content-type': 'application/json',
                        'x-pushbots-appid': self.app_id,
                        'x-pushbots-secret': self.app_secret}
    def del_token(self, token):
        url = 'https://api.pushbots.com/deviceToken/del'
        if settings.CELERY_USE:
            del_pushbot_token.delay(url=url, data=json.dumps({'token': token, 'platform': "0"}), headers=self.headers)
        else:
            del_pushbot_token(url=url, data=json.dumps({'token': token, 'platform': "0"}), headers=self.headers)

