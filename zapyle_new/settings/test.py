PUSH_NOTIF_DOMAIN = 'test.zapyle.com'



from common import *

connect('test_zapyle', username='test_zapyle', password='zapyle')

WSGI_APPLICATION = 'zapyle_new.wsgi.wsgi_test.application'
CURRENT_DOMAIN = 'http://test.zapyle.com'
STATIC_ROOT =  'https://s3-us-west-1.amazonaws.com/hellozapyle'
MEDIA_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_media")
SHIPPING_CHARGE = 2
INSTAGRAM_REDIRECT_URI = 'http://localhost:9000/'
FB_REDIRECT_URI = 'http://localhost:9000/'
DEFAULT_FROM_EMAIL = 'info@test.zapyle.com'
SERVER_EMAIL = 'error@test.zapyle.com'
FROM_EMAIL = 'hello@zapyle.com'
OTP_MSG = "Test OTP is {}. Please enter this OTP at login. Love, Zapyle Team"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# STATIC_URL = '/zapstatic/'
AWS_DEFAULT_ACL = ''
AWS_ACCESS_KEY_ID = 'AKIAIED4VMZB2L3OPY4A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'hellozapyle'

AWS_S3_CUSTOM_DOMAIN = '%s.s3-website-us-west-1.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'Cache-Control': 'max-age=94608000',
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zapyle_db',
        'USER': 'zapadmin',
        'PASSWORD': 'zapy!e1234',
        'HOST': 'zapyledb.cijbxbnbcn1g.us-west-1.rds.amazonaws.com',
        'PORT': '5432'
    }
}

ZAP_ENV = 'TEST'
DEBUG = True
ALLOWED_HOSTS = ['.zapyle.com', '.citruspay.com']
APPVIRALITY_ENABLE = True

MONGO_DB_TRACKER = False
CELERY_USE = True
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS += ('corsheaders',)

try:
    from private import *
except ImportError:
    pass




# from common import *

# connect('test_zapyle', username='test_zapyle', password='zapyle')

# WSGI_APPLICATION = 'zapyle_new.wsgi.wsgi_test.application'
# CURRENT_DOMAIN = 'http://test.zapyle.com'
# STATIC_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_static")
# MEDIA_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_media")
# SHIPPING_CHARGE = 2
# INSTAGRAM_REDIRECT_URI = 'http://localhost:9000/'
# FB_REDIRECT_URI = 'http://localhost:9000/'
# DEFAULT_FROM_EMAIL = 'info@test.zapyle.com'
# SERVER_EMAIL = 'error@test.zapyle.com'
# FROM_EMAIL = 'hello@test.zapyle.com'
# OTP_MSG = "Test OTP is {}. Please enter this OTP at login. Love, Zapyle Team"
# ZAP_ENV = 'PRODUCTION'
# TORNADO_USE = True
# TORNADO_URL = 'http://testsocket.zapyle.com/odanrot'
# DEBUG = False
# ALLOWED_HOSTS = ['*']
# APPVIRALITY_ENABLE = True
# MONGO_DB_TRACKER = True
# CELERY_USE = True
# CORS_ORIGIN_ALLOW_ALL = True
# MIDDLEWARE_CLASSES = (
#     'zap_apps.account.zap_middleware.TestMid',
#     'zap_apps.account.zap_middleware.DisableCSRFOnDebug',
#     # 'zap_apps.account.zap_middleware.DisableCSRFForCitrus',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     # 'zap_apps.account.zap_middleware.CheckSuperUser',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
# )

# INSTALLED_APPS += ('corsheaders',)


# try:
# 	from private import *
# except ImportError:
# 	pass
	
# import psycopg2
# with open(BASE_DIR + "/settings/sqlsequencefix.sql", "r") as fix:
#     conn = psycopg2.connect("dbname = '{}' user = '{}' host = 'localhost' password = '{}'".format(
#         DATABASES['default']['NAME'],
#         DATABASES['default']['USER'],
#         DATABASES['default']['PASSWORD']))
#     cur = conn.cursor()
#     cur.execute(fix.read())
#     conn.commit()






