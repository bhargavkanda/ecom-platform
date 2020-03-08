from common import *
BROKER_URL = 'amqp://zapyle:Zapyle1234@localhost:5672//'
WSGI_APPLICATION = 'zapyle_new.wsgi.wsgi_prod.application'
ALLOWED_HOSTS = ['.zapyle.com', '.citruspay.com', 'www.zapyle.com']
STATIC_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_static")
MEDIA_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_media")
ZAP_ENV = 'PRODUCTION'
DEBUG = False
DEFAULT_FROM_EMAIL = "info@zapyle.com"
FROM_EMAIL = 'hello@zapyle.com'
SERVER_EMAIL = "errors@zapyle.com"
OTP_MSG = "OTP for your phone number verification is {}. Love, Zapyle Team"
LANDING_PAGE = False
EASTER_REFERRAL = False
ZAPCASH_REFERRAL = 100
ELASTIC_INDEX = True
ELASTIC_INDEX_NAME = "production_ninenine/"
ELASTIC_URL = 'https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/shafi/products/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
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

AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'Cache-Control': 'max-age=94608000',
}

# AWS_STORAGE_BUCKET_NAME = 'zap-static'
# AWS_S3_CUSTOM_DOMAIN = '%s.s3-website.ap-south-1.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
# STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# AWS_S3_HOST = 'http://zap-static.s3-website.ap-south-1.amazonaws.com/'

CELERY_USE=True
OTP_DISABLE = True
TORNADO_URL = 'http://prodsocket.zapyle.com/odanrot'
PUSH_NOTIFICATION_ENABLE = True
EMAIL_NOTIFICATION_ENABLE = True
SMS_NOTIFICATION_ENABLE = True
PARCEL_CHECK_ENABLED = False
SENDIN_BLUE_ACCESS_KEY = '0d5T87PH6ALmca43'

PUSH_NOTIFICATIONS_SETTINGS = {
       "GCM_API_KEY": "AIzaSyDVvrcs1ezmWRX_jiaz5flXwIHoos3lOn8",
       # "GCM_API_KEY": "AIzaSyDHOeH8pyK61d4TBTn9J3rXTwi3_556_UQ",
       #"APNS_CERTIFICATE": "/path/to/your/certificate.pem",
}
SHIPPING_CHARGE = 99
# PUSHBOT_ID = "56e2a8c31779597a188b4567"
# PUSHBOT_SECRET = "427394288bb151ea4ca6ed434d7b12c2"
PUSHBOT_ID = "55d3021b17795969478b4569"
PUSHBOT_SECRET = "b66ee0e7be3d827c85e3343c3d42f96a"
MVC_ISSUE_URL = 'https://coupons.citruspay.com/cms_api.asmx/IssueCoupons'
MVC_REDEEM_URL = 'https://coupons.citruspay.com/cms_api.asmx/RedeemCampaign'
MVC_ROLL_BACK_URL = 'https://coupons.citruspay.com/cms_api.asmx/RollbackCampaign'
MVC_BALANCE_URL = 'https://coupons.citruspay.com/cms_api.asmx/FetchCampaignBalance'
MVC_PARTNER_ID = 'cqoos6l2u2'
MVC_PASSWORD = 'R05H4Q7GB1XX3SWQ98IF'
MVC_MERCHANT_ID = 'cqoos6l2u2'
#CITRUS
MERCHANT_ACCESS_KEY = "R05H4Q7GB1XX3SWQ98IF"
MERCHANT_SECRET_KEY = "751652eeac5c9a98a1203d04a1cadd9edb956d80"
MERCHANT_VANITY_URL = 'cqoos6l2u2'
CITRUS_SIGNIN_ID = 'cqoos6l2u2-signin'
CITRUS_SIGNIN_CLIENT_SECRET = 'afee8d44e739705c7d7c347d0c3d89d4'
CITRUS_SIGNUP_ID = 'cqoos6l2u2-signup'
CITRUS_SIGNUP_CLIENT_SECRET =  '2268ae0137ab1fadb1f83235cf23847a'
CITRUS_JS_SIGNIN_ID = 'cqoos6l2u2-JS-signin'
CITRUS_JS_SIGNUP_ID = '112b13d6297c4a9a476fb833b7b12b93'
CITRUS_CASH_REFUND_URL = 'https://admin.citruspay.com/service/v2/prerefund/refund'
CITRUS_CASH_PAY_URL = 'https://admin.citruspay.com/service/v2/prepayment/prepaid_pay'
CITRUS_CASH_BALANCE_URL = 'https://admin.citruspay.com/service/v2/prepayment/balance'
CITRUS_ENQUIRY_URL = 'https://admin.citruspay.com/api/v2/txn/enquiry/'

CITRUS_GET_SAVED_CARD_URL = 'https://admin.citruspay.com/service/v2/profile/me/payment'
CITRUS_SIGNIN_TOKEN_URL = 'https://admin.citruspay.com/oauth/token'
CITRUS_SIGNUP_TOKEN_URL = 'https://admin.citruspay.com/oauth/token'
CITRUS_SIGNUP_URL = 'https://admin.citruspay.com/service/um/link/user/extended'
CITRUS_ENV = 'PRODUCTION'
DEFAULT_HTTP_PROTOCOL = 'https'


CITRUS_MRK_AUTH_URL = "https://splitpay.citruspay.com/marketplace/auth/"
CITRUS_MRK_SELLER_URL = 'https://splitpay.citruspay.com/marketplace/seller/'
CITRUS_MRK_SPLIT_URL = 'https://splitpay.citruspay.com/marketplace/split/'
CITRUS_MRK_RELEASE_URL = 'https://splitpay.citruspay.com/marketplace/funds/release/'

CITRUS_REFUND_URL = 'https://admin.citruspay.com/api/v2/txn/refund'

DOMAIN_NAME = 'https://www.zapyle.com'
CURRENT_DOMAIN = 'https://prod.zapyle.com'
PUSH_NOTIF_DOMAIN = 'prod.zapyle.com'

TORNADO_USE = True
TORNADO_URL = 'http://prodsocket.zapyle.com/odanrot'

#ARAMEX
ARAMEX_SERVICE = True
ARAMEX_BASE_URL = 'https://ws.aramex.net'


ARAMEX_USERNAME = "likhita@zapyle.com"
ARAMEX_PASSWORD = "Aramex123"
ARAMEX_VERSION = "v1"
ARAMEX_ACCOUNT_NUMBER = "70001814"
ARAMEX_ACCOUNT_PIN = "216216"
ARAMEX_ACCOUNT_ENTITY = "BLR"
ARAMEX_ACCOUNT_COUNTRY_CODE = "IN"
ARAMEX_SOURCE = 24


#DELHIVERY
DELHIVERY_BASE_URL = 'https://track.delhivery.com'
DELHIVERY_API_KEY = 'b5944330ef5e20dd66ae9aacfaf589a49ff28171'
DELHIVERY_PICKUP_NAME = 'ZAPYLE - DFS'

JUSPAY_ENV = 'production'
JUSPAY_API_KEY = 'B9609E37792544B083C40F86BC4BB26A'

#PARCELLED
PARCELLED_API_KEY = '_Cl6nADizsWuKHWOl-34bg'
PARCELLED_BASE_URL = 'http://parcelled.in/api/v1/'

WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

BULK_NOTIFICTAION_QUEUE = 'test_push_queue'
BULK_NOTIFICTAION_RESP_QUEUE = 'test_push_response_queue'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}

ZAPYLE_BILL_EMAIL = ['likhita@zapyle.com','neha@zapyle.com']

APPVIRALITY_ENABLE = True

try:
    from private import *
except ImportError:
    pass
from os import listdir
from os.path import isfile, join
onlyfiles = [join(BASE_DIR + "/settings/sqlfixes/", f) for f in listdir(BASE_DIR + "/settings/sqlfixes") if isfile(join(BASE_DIR + "/settings/sqlfixes/", f))]

import psycopg2
for i in onlyfiles:
    with open(i, "r") as fix:
        conn = psycopg2.connect("dbname = '{}' user = '{}' host = 'localhost' password = '{}'".format(
            DATABASES['default']['NAME'],
            DATABASES['default']['USER'],
            DATABASES['default']['PASSWORD']))
        cur = conn.cursor()
        try:
            cur.execute(fix.read())
        except:
            continue
        conn.commit()
