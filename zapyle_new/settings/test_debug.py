from common import *

connect('test_zapyle', username='test_zapyle', password='zapyle')

WSGI_APPLICATION = 'zapyle_new.wsgi.wsgi_test.application'
CURRENT_DOMAIN = 'localhost:9000'
STATIC_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_static")
MEDIA_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_media")
SHIPPING_CHARGE = 2
INSTAGRAM_REDIRECT_URI = 'http://localhost:9000/'
FB_REDIRECT_URI = 'http://localhost:9000/'
DEFAULT_FROM_EMAIL = 'info@test.zapyle.com'
SERVER_EMAIL = 'error@test.zapyle.com'
FROM_EMAIL = 'hello@test.zapyle.com'
OTP_MSG = "Test OTP is {}. Please enter this OTP at login. Love, Zapyle Team"
ZAP_ENV = 'LOCAL'
TORNADO_USE = True
TORNADO_URL = 'http://testsocket.zapyle.com/odanrot'
ALLOWED_HOSTS = ['.zapyle.com', '.citruspay.com']
APPVIRALITY_ENABLE = True
PUSH_NOTIFICATION_ENABLE = True
MONGO_DB_TRACKER = False
CELERY_USE = False

ADMINS = (
	('Latheef', 'latheef@zapyle.com'),
	)
try:
	from private import *
except ImportError:
	pass
