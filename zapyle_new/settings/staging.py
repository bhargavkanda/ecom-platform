from common import *
WSGI_APPLICATION = 'zapyle_new.wsgi.wsgi_staging.application'
ALLOWED_HOSTS = ['.zapyle.com', '.citruspay.com']
STATIC_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_static")
MEDIA_ROOT =  os.path.join(os.path.dirname(BASE_DIR), "zap_media")
DEBUG = False
DEFAULT_FROM_EMAIL = "info@staging.zapyle.com"
FROM_EMAIL = 'hello@staging.zapyle.com'
SERVER_EMAIL = "error@staging.zapyle.com"
SHIPPING_CHARGE = 2
EASTER_REFERRAL = True
TORNADO_URL = 'http://testsocket.zapyle.com/odanrot'

MIDDLEWARE_CLASSES = (
    'zap_apps.account.zap_middleware.TestMid',
    'zap_apps.account.zap_middleware.DisableCSRFOnDebug',
    # 'zap_apps.account.zap_middleware.DisableCSRFForCitrus',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'zap_apps.account.zap_middleware.CheckSuperUser',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)	
CORS_ORIGIN_ALLOW_ALL = True
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
        'NAME': 'zapyle_db_staging',
        'USER': 'zapadmin_staging',
        'PASSWORD': 'zapy!e1234',
        'HOST': 'localhost',
    }
}
connect('staging_zapyle', username='staging_zapyle', password='zapyle')
OTP_DISABLE = True
CELERY_USE=True
PUSH_NOTIFICATION_ENABLE = False
EMAIL_NOTIFICATION_ENABLE = False
SMS_NOTIFICATION_ENABLE = False
OTP_MSG = "Test OTP is {}. Please enter this OTP at login. Love, Zapyle Team"
ZAP_ENV = 'PRODUCTION'
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
#CITRUS
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

CITRUS_GET_SAVED_CARD_URL = 'https://admin.citruspay.com/service/v2/profile/me/payment'
CITRUS_SIGNIN_TOKEN_URL = 'https://admin.citruspay.com/oauth/token'
CITRUS_SIGNUP_TOKEN_URL = 'https://admin.citruspay.com/oauth/token'
CITRUS_SIGNUP_URL = 'https://admin.citruspay.com/service/um/link/user/extended'
CITRUS_ENV = 'PRODUCTION'

CITRUS_MRK_AUTH_URL = "https://splitpay.citruspay.com/marketplace/auth/"
CITRUS_MRK_SELLER_URL = 'https://splitpay.citruspay.com/marketplace/seller/'
CITRUS_MRK_SPLIT_URL = 'https://splitpay.citruspay.com/marketplace/split/'
CITRUS_MRK_RELEASE_URL = 'https://splitpay.citruspay.com/marketplace/funds/release/'


CURRENT_DOMAIN = 'http://staging.zapyle.com'
#SQLFIX
import psycopg2
with open(BASE_DIR + "/settings/sqlsequencefix.sql", "r") as fix:
    conn = psycopg2.connect("dbname = '{}' user = '{}' host = 'localhost' password = '{}'".format(
        DATABASES['default']['NAME'],
        DATABASES['default']['USER'],
        DATABASES['default']['PASSWORD']))
    cur = conn.cursor()
    cur.execute(fix.read())
    conn.commit()


#DELHIVERY
DELHIVERY_BASE_URL = 'https://track.delhivery.com'
DELHIVERY_API_KEY = 'b5944330ef5e20dd66ae9aacfaf589a49ff28171'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

PARCELLED_API_KEY = '_Cl6nADizsWuKHWOl-34bg'
PARCELLED_BASE_URL = 'http://parcelled.in/api/v1/'
