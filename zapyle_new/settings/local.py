from common import *

connect('test_zapyle', username='test_zapyle', password='zapyle')

WSGI_APPLICATION = 'zapyle_new.wsgi.wsgi_local.application'
CURRENT_DOMAIN = 'http://dev.zapyle.com'
STATIC_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_static")
MEDIA_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_media")
SHIPPING_CHARGE = 2
INSTAGRAM_REDIRECT_URI = 'http://localhost:9000/'
FB_REDIRECT_URI = 'http://localhost:9000/'
DEFAULT_FROM_EMAIL = 'info@test.zapyle.com'
SERVER_EMAIL = 'error@test.zapyle.com'
FROM_EMAIL = 'hello@zapyle.com'
OTP_MSG = "Test OTP is {}. Please enter this OTP at login. Love, Zapyle Team"
ELASTIC_INDEX = True
ELASTIC_INDEX_NAME = "dev_products/"

ZAP_ENV = 'LOCAL'
DEBUG = True
ALLOWED_HOSTS = ['.zapyle.com', '.citruspay.com']
APPVIRALITY_ENABLE = True

MONGO_DB_TRACKER = False
CELERY_USE = True
CORS_ORIGIN_ALLOW_ALL = True
TORNADO_URL = 'http://localhost:8888/odanrot'
try:
	from private import *
except ImportError:
	pass

