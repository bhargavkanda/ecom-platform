import requests
import json
from django.conf import settings


class Slack:
	def __init__(self):
		self.url = settings.SLACK_INCOMING_WEBHOOK_URL
	def post_msg(self, msg, img_url, icon_url, product_page):
		d = {
			"channel": "#general",
			"username": "OrderBot",
			"icon_url": icon_url,
			"text": product_page,
		    "attachments": [
		        {
		            "fields": [
		                {
		                    "title": msg,
		                    ""
		                    "short": False
		                }
		            ],
		            "image_url": 'https://www.zapyle.com{}'.format(img_url),
		        }
		    ]
		}
		requests.post(url=self.url, data=json.dumps(d))
