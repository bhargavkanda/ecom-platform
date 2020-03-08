import requests
from django.conf import settings
import json
# from zap_apps.payment.views import zap_bill_generator


class CitrusCash(object):

    def __init__(self, email, mob_no=None):
        self.email = email
        self.mob_no = mob_no
        self.CITRUS_SIGNIN_ID = settings.CITRUS_SIGNIN_ID
        self.CITRUS_SIGNIN_CLIENT_SECRET = settings.CITRUS_SIGNIN_CLIENT_SECRET
        self.CITRUS_SIGNUP_ID = settings.CITRUS_SIGNUP_ID
        self.CITRUS_SIGNUP_CLIENT_SECRET = settings.CITRUS_SIGNUP_CLIENT_SECRET
        self.CITRUS_JS_SIGNIN_ID = settings.CITRUS_JS_SIGNIN_ID

    def refund(self, amount, tr_ref_id, comment):
        url = settings.CITRUS_CASH_REFUND_URL
        signin_token = get_signin_token(
            self.CITRUS_SIGNIN_ID, self.CITRUS_SIGNIN_CLIENT_SECRET, self.email)
        resp = requests.post(
            url=url,
            data={
                'customer': self.email,
                'amount': amount,
                "currency": 'INR',
                "paymentId": tr_ref_id,
                "comment": comment
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'bearer {}'.format(signin_token),
            },
            verify=False
        )
        return resp.json()

    def balance(self):
        url = settings.CITRUS_CASH_BALANCE_URL
        try:
            signin_token = get_signin_token(
                self.CITRUS_SIGNIN_ID, self.CITRUS_SIGNIN_CLIENT_SECRET, self.email)
        except:
            signup_token = get_signup_token(
                self.CITRUS_SIGNUP_ID, self.CITRUS_SIGNUP_CLIENT_SECRET)
            get_signup_user(self.email, signup_token, self.mob_no)
        signin_token = get_signin_token(
            self.CITRUS_SIGNIN_ID, self.CITRUS_SIGNIN_CLIENT_SECRET, self.email)
        headers = {'Authorization': 'bearer {}'.format(
            signin_token), 'Content-Type': 'application/json'}
        resp = requests.get(url=url, headers=headers, verify=False)
        print resp.json()
        return resp.json()

    def pay(self, req, amount, notify_url="", c_params={}):
        from zap_apps.payment.views import zap_bill_generator
        bill = zap_bill_generator(req, amount)
        signin_token = get_signin_token(
            self.CITRUS_SIGNIN_ID, self.CITRUS_SIGNIN_CLIENT_SECRET, self.email)
        url = settings.CITRUS_CASH_PAY_URL
        if notify_url:
            bill['notifyUrl'] = notify_url
        if c_params:
            bill['customParameters'] = c_params
        resp = requests.post(
            url=url,
            data=json.dumps(bill),
            headers={'Authorization': 'bearer {}'.format(
                signin_token), 'Content-Type': 'application/json'},
            verify=False
        )
        return resp.json()


def get_saved_cards(signin_id, client_secret, email):
    access_token = get_signin_token(signin_id, client_secret, email)
    url = settings.CITRUS_GET_SAVED_CARD_URL
    headers = {'Authorization': 'bearer {}'.format(
        access_token), 'Content-Type': 'application/json'}
    resp = requests.get(url=url, headers=headers, verify=False)
    return resp.json()


def get_signin_token(signin_id, client_secret, email):
    url = settings.CITRUS_SIGNIN_TOKEN_URL
    resp = requests.post(
        url=url,
        data={
            'client_id': signin_id,
            'client_secret': client_secret,
            "grant_type": 'username',
            'username': email
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        verify=False
    )
    print resp.text

    return resp.json()['access_token']


def get_signup_user(email, access_token, mob_no):
    url = settings.CITRUS_SIGNUP_URL
    resp = requests.post(
        url=url,
        data=json.dumps(
            {'email': email, 'mobile': mob_no}),
        headers={'Authorization': 'bearer {}'.format(
            access_token), 'Content-Type': 'application/json'},
        verify=False
    )
    print resp.text, mob_no
    return resp.json()


def get_signup_token(signup_id, client_secret):
    url = settings.CITRUS_SIGNUP_TOKEN_URL
    resp = requests.post(
        url=url,
        data={
            'client_id': signup_id,
            'client_secret': client_secret,
            "grant_type": 'implicit'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        verify=False
    )
    return resp.json()['access_token']
