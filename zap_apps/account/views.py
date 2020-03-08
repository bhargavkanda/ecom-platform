from django.shortcuts import render
import requests
import json
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.conf import settings
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from zap_apps.zapuser.models import ZapUser, LoggedFrom, UserProfile, LoggedDevice, WebsiteLead
from zap_apps.account.models import Otp, Testimonial
from zap_apps.account.account_serializer import (FbUserSlzr, InstagramUserSlzr, AccestokenSerializar,
                                                 AccestokenSerializar, ZapLoginUserSlzr, ZapSignupUserSlzr,
                                                 LoggedFromSerializar, ResetPasswordSrlzr, ZapEmailSlzr,
                                                 OTPResetPasswordSrlzr,
                                                 ZapReducedSignupUserSlzr)

import requests
import re
from django.db.models import Q
from zap_apps.zapuser.zapuser_serializer import PhoneNumSrlzr, PhoneNumWithOtpSrlzr, PhoneNumSrlzrOTP, check_phone_number
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import base36_to_int, int_to_base36
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from zap_apps.account import account_activities
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import Http404
from zap_apps.zapuser.models import ZAPGCMDevice, LoggedDevice
from zap_apps.account.models import AppLinkSms, CallRequest
import requests
from zap_apps.zap_notification.views import ZapSms, ZapEmail
from django.contrib.auth.models import User
from zap_apps.referral.models import RefCode
from zap_apps.extra_modules.zap_pushbot import ZapPushbot
from django import forms
from django.template.loader import render_to_string
import pdb


class NameForm1(forms.Form):
    name = forms.CharField(label='name', min_length=3, max_length=30)
    phone = forms.RegexField(regex=r'^\d{10,15}$',
                             error_message=("Phone number contain 10 digits."))
    email = forms.EmailField(label='email', max_length=50)


# Create your views here.
def create_gcm_device(reg_id, user, platform=None, app_version=None):
    # if logged_device.name == "ios":
    #     try:
    #         z = ZapPushbot()
    #         for i in ZAPGCMDevice.objects.filter(user__zapuser=user, logged_device=logged_device):
    #             if not i.registration_id == reg_id:
    #                 z.del_token(i.registration_id)
    #                 i.delete()
    #     except:
    #         pass
    # else:
    # pdb.set_trace()
    try:
        ZAPGCMDevice.objects.filter(
            registration_id=reg_id).delete()
    except:
        pass
    if platform and reg_id:
        logged_device = LoggedDevice.objects.get(name=platform.lower())

        gcm, c = ZAPGCMDevice.objects.get_or_create(
            registration_id=reg_id, user=user, logged_device=logged_device)
        if app_version:
            gcm.app_version = app_version
            gcm.save()


@ensure_csrf_cookie
def home(request, page=None):
    # if getattr(settings, "LANDING_PAGE", False):
    #     data = {}
    #     if request.method == 'POST':
    #         if 'phone_number' in request.POST:
    #             phone = request.POST.get('phone_number', '')
    #             try:
    #                 p = int(phone)
    #                 full_nums = str(p)[-10:]
    #                 if len(full_nums) >= 10:
    #                     sms = ZapSms()
    #                     sms.send_sms(full_nums,
    #                                  'Congratulations on your first step to %23MajorClosetGoals! Download Zapyle using this link: https://bnc.lt/goto-zapyle-app. Happy Shopping! Love, The Zapyle Team')
    #                     AppLinkSms.objects.create(phone=str(p)[-10:])
    #                     return JsonResponse({'status': 'success', 'data': 'A link to download the Zapyle app has been sent to your mobile. Click on it and enter the world of luxury fashion!'})
    #                 else:
    #                     data = {'phone': phone, 'error': 'Please enter a valid phone number'}
    #             except (ValueError, TypeError):
    #                 data = {'phone': phone, 'error': 'Please enter a valid phone number'}
    #             return JsonResponse({'status': 'error', 'errors': data})
    #         else:
    #             datas = request.POST
    #             if 'phone' in datas:
    #                 form = NameForm1(datas)
    #                 if form.is_valid():
    #                     CallRequest.objects.create(name=datas['name'], email=datas['email'], phone=datas['phone'])
    #                     return JsonResponse({'status': 'success'})
    #                 else:
    #                     errors = form.errors
    #                     return JsonResponse({'status': 'error', 'errors': errors})
    #             else:
    #                 return JsonResponse({'status': 'error'})
    #     else:
    #         data = {}
    #     return render(request, 'landing/home.html', data)
    # else:
    if request.method == 'GET':
        # print '---------------------------------------------------------------------------------------------'
        #return render(request, 'account/home.html')
        
        return render(
            request,
            'account/home.html',
            {
                # 'INSTAGRAM_CLIENT_ID': settings.INSTAGRAM_CLIENT_ID,
                # 'FB_CLIENT_ID': settings.FB_CLIENT_ID,
                # 'ZAP_ENV': settings.ZAP_ENV,
                'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION,
                'image_header':True,
                'page': page
                # 'h_d' : WebsiteHeaderProducts()
            }
        )
    else: #POST
        data = {}
        if 'phone_number' in request.POST:
            phone = request.POST.get('phone_number', '')
            try:
                p = int(phone)
                full_nums = str(p)[-10:]
                if len(full_nums) >= 10:
                    sms = ZapSms()
                    sms.send_sms(full_nums,
                                 'Congratulations on your first step to %23MajorClosetGoals! Download Zapyle using this link: https://bnc.lt/goto-zapyle-app. Happy Shopping! Love, The Zapyle Team')
                    AppLinkSms.objects.create(phone=str(p)[-10:])
                    return JsonResponse({'status': 'success', 'data': 'A link to download the Zapyle app has been sent to your mobile. Click on it and enter the world of luxury fashion!'})
                else:
                    data = {'phone': phone, 'error': 'Please enter a valid phone number'}
            except (ValueError, TypeError):
                data = {'phone': phone, 'error': 'Please enter a valid phone number'}
        return JsonResponse({'status': 'error', 'errors': data})

from django.utils import timezone
from zap_apps.discover.models import Homefeed
from zap_apps.discover.discover_serializer import HomefeedSerializer
@ensure_csrf_cookie
def home_jinja2(request, page=None):
    if request.method == 'GET':
        return render(
            request,
            'account/elastic_home.html',
            {
                'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION,
                'image_header':True,
                'page': page
            }
        )


def get_session_id(request):
    if not request.session.session_key:
        request.session.cycle_key()
    return request.session.session_key


def referral(request):
    return JsonResponse(
        {'status': getattr(settings, "EASTER_REFERRAL", False)}
    )


def download(request):
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = get_current_site(request)
    domain = "{0}://{1}".format(
        protocol,
        current_site.domain
    )
    download_link = domain + settings.MEDIA_URL + 'app-production-debug.apk'
    return render(
        request,
        'download.html',
        {'download_link': download_link}
    )


class ZapLogin(ZapView):
    def get_instagram_user_data(self, access_token):
        url = "https://api.instagram.com/v1/users/self/?access_token={}".format(
            access_token)
        res = requests.get(url)
        return res.json()['data'] if res.json().get('data') else {}

    def get_fb_user_data(self, access_token):
        url = "https://graph.facebook.com/v2.5/me?access_token={}&fields=id,first_name,last_name,name,email".format(
            access_token)
        res = requests.get(url)
        return res.json()

    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True
            # Redirect to a success page.

        else:
            return False

    def post(self, request, format=None):
        if request.user.is_authenticated():
            if not hasattr(request.user, 'zapuser'):
                logout(request)
                pass
            else:
                return self.send_response(1, {
                    'email': request.user.email,
                    'username': request.user.username,
                    'session_id': get_session_id(request),
                    'profile_completed': request.user.profile.profile_completed
                })
        data = request.data.copy()
        req = LoggedFromSerializar(data=data)
        app_version = request.COOKIES.get('VER', None)
        if not req.is_valid():
            return self.send_response(0, req.errors)
        if data['logged_from'] == 'fb':
            req = AccestokenSerializar(data=data)
            if not req.is_valid():
                return self.send_response(0, req.errors)
            user_details = self.get_fb_user_data(data['access_token'])
            req = FbUserSlzr(data=user_details)
            if not req.is_valid():
                return self.send_response(0, "incorrect access_token!")
            user_details['fb_id'] = user_details['id']
            lf = LoggedFrom.objects.get(name="fb")
            try:
                user = ZapUser.objects.get(fb_id=user_details['fb_id'])
                new_user = False
            except ZapUser.DoesNotExist:
                new_user = True
                user = ZapUser(fb_id=user_details[
                    'fb_id'], username=get_random_string(15), logged_from=lf)
                profile_pic = "https://graph.facebook.com/" + \
                              user_details['fb_id'] + "/picture?type=large"
                user.first_name = user_details[
                    'first_name'] if user_details.get('first_name') else ""
                user.last_name = user_details[
                    'last_name'] if user_details.get('last_name') else ""
                if user_details.get('email') and not ZapUser.objects.filter(email=user_details['email']).exists():
                    user.email = user_details['email']
                user.logged_device = LoggedDevice.objects.get(
                    name=data['logged_device'])
                user.save()
                # issue_wallet_for_signup(user)
                up, c = UserProfile.objects.get_or_create(user=user)
                user.profile.profile_pic = profile_pic
                user.profile.save()
            if self.auth_login({'fb_id': user_details['fb_id']}):
                if data['logged_device'] in ['ios', "android"]:
                    create_gcm_device(data['gcm_reg_id'], user, platform=request.PLATFORM, app_version=app_version)
                return self.send_response(1, {'session_id': get_session_id(request), 'new_user': new_user,
                                              'profile_completed': request.user.profile.profile_completed})
        if data['logged_from'] == 'instagram':
            req = AccestokenSerializar(data=data)
            if not req.is_valid():
                return self.send_response(0, req.errors)
            user_details = self.get_instagram_user_data(data['access_token'])
            req = InstagramUserSlzr(data=user_details)
            if not req.is_valid():
                return self.send_response(0, "incorrect access_token!")
            lf = LoggedFrom.objects.get(name="instagram")
            try:
                user = ZapUser.objects.get(instagram_id=user_details['id'])
            except ZapUser.DoesNotExist:
                try:
                    user = ZapUser.objects.get(username=user_details['username'])
                    user.instagram_id = user_details['id']
                    user.save()
                except ZapUser.DoesNotExist:
                    user = ZapUser(instagram_id=user_details[
                        'id'], username=get_random_string(15), logged_from=lf)
                    user.first_name = user_details['username'] if user_details.get('username') else user_details[
                        'full_name'] if user_details.get('full_name') else user_details['username'] if user_details.get(
                        'first_name') else ""
                    user.last_name = user_details[
                        'last_name'] if user_details.get('last_name') else ""
                    user.logged_device = LoggedDevice.objects.get(
                        name=data['logged_device'])
                    user.save()
                    up, c = UserProfile.objects.get_or_create(user=user)
                    user.profile.profile_pic = user_details[
                        'profile_picture'] if user_details.get('profile_picture') else ""
                    user.profile.save()
            if self.auth_login({'instagram_id': user_details['id']}):
                if data['logged_device'] in ['ios', "android"]:
                    create_gcm_device(data['gcm_reg_id'], user, platform=request.PLATFORM, app_version=app_version)
                return self.send_response(1, {'session_id': get_session_id(request),
                                              'profile_completed': request.user.profile.profile_completed})
        if data['logged_from'] == 'zapyle':
            req = ZapLoginUserSlzr(data=data)
            if not req.is_valid():
                return self.send_response(0, req.errors)
            if self.auth_login({'email': data['email'], 'password': data['password']}):
                if data['logged_device'] in ['ios', "android"]:
                    try:
                        user = ZapUser.objects.get(email=data['email'])
                    except ZapUser.DoesNotExist:
                        user = ZapUser.objects.get(zap_username=data['email'])
                    create_gcm_device(data['gcm_reg_id'], user, platform=request.PLATFORM, app_version=app_version)
                    user.logged_device = LoggedDevice.objects.get(
                        name=data['logged_device'])
                    user.save()
                return self.send_response(1, {'session_id': get_session_id(request),
                                              'profile_completed': request.user.profile.profile_completed})
        return self.send_response(0, 'Username/Email and password do not match.')


class InstagramRedirectView(ZapView):
    def get_domain(self, url):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}{2}".format(
            protocol,
            current_site.domain,
            url
        )

    def get(self, request, format=None):
        url = "https://instagram.com/oauth/authorize/?client_id={}&redirect_uri={}&response_type=code".format(
            settings.INSTAGRAM_CLIENT_ID,
            self.get_domain("/account/instagram/checkoutlogin/") if request.GET.get(
                'from') == 'checkout' else self.get_domain('/account/instagram/login/'))
        return HttpResponseRedirect(url)


class ZapLogout(ZapAuthView):
    def un_reg(self, token):
        try:
            requests.put(
                url='https://api.pushbots.com/deviceToken/del',
                data=json.dumps({'token': token, "platform": '0'}),
                headers={
                    'x-pushbots-appid': settings.PUSHBOT_ID,
                    'Content-Type': 'application/json'
                }
            )
        except:
            pass

    def get(self, request, format=None):
            # ZAPGCMDevice.objects.filter(
            #     registration_id=request.GET['reg_id']).delete()
            # self.un_reg(request.GET['reg_id'])
        logout(request)
        if request.GET.get('reg_id'):
            z = ZapPushbot()
            z.del_token(request.GET['reg_id'])
        return self.send_response(1, "Successfully Logged out")


class InstagramCheckoutLogin(ZapView):
    # def get_instagram_user_data(self, access_token):
    #     url = "https://api.instagram.com/v1/users/self/?access_token={}".format(access_token)
    #     res = requests.get(url)
    # return res.json()['data']
    # def get_instagram_user_data(self, access_token):
    #     url = "https://api.instagram.com/v1/users/self/?access_token={}".format(access_token)
    #     res = requests.get(url)
    #     return res.json()['data'] if res.json().get('data') else {}

    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True
            # Redirect to a success page.

        else:
            return False

    def get_domain(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}{2}".format(
            protocol,
            current_site.domain,
            "/account/instagram/checkoutlogin/"
        )

    def get(self, request, format=None):
        code = request.data.get('code') or request.GET.get('code') or ""
        to_post = {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            # 'redirect_uri': re.match('(.*)\?', request.build_absolute_uri()).group(1),
            'redirect_uri': self.get_domain(),
            'code': code
        }
        res = requests.post(
            url="https://api.instagram.com/oauth/access_token", data=to_post)
        user_details = res.json()['user']
        lf = LoggedFrom.objects.get(name="instagram")
        try:
            user = ZapUser.objects.get(instagram_id=user_details['id'])
            user.profile.profile_completed = 5
            user.save()
        except ZapUser.DoesNotExist:
            try:
                user = ZapUser.objects.get(username=user_details['username'])
                user.instagram_id = user_details['id']
                user.profile.profile_completed = 5
                user.save()
            except ZapUser.DoesNotExist:
                user = ZapUser(instagram_id=user_details[
                    'id'], username=get_random_string(15), logged_from=lf)
                user.first_name = user_details['first_name'] if user_details.get('first_name') else user_details[
                    'full_name'] if user_details.get('full_name') else user_details['username'] if user_details.get(
                    'username') else ""
                user.last_name = user_details[
                    'last_name'] if user_details.get('last_name') else ""
                user.save()
                up, c = UserProfile.objects.get_or_create(user=user)
                user.profile.profile_pic = user_details[
                    'profile_picture'] if user_details.get('profile_picture') else ""
                user.profile.profile_completed = 5
                user.profile.save()
        if self.auth_login({'instagram_id': user.instagram_id}):
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
            return HttpResponseRedirect("/#/checkout")
        return HttpResponseRedirect("/")


class InstagramLogin(ZapView):
    # def get_instagram_user_data(self, access_token):
    #     url = "https://api.instagram.com/v1/users/self/?access_token={}".format(access_token)
    #     res = requests.get(url)
    # return res.json()['data']
    # def get_instagram_user_data(self, access_token):
    #     url = "https://api.instagram.com/v1/users/self/?access_token={}".format(access_token)
    #     res = requests.get(url)
    #     return res.json()['data'] if res.json().get('data') else {}

    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True
            # Redirect to a success page.

        else:
            return False

    def get_domain(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}{2}".format(
            protocol,
            current_site.domain,
            "/account/instagram/login/"
        )

    def get(self, request, format=None):
        code = request.data.get('code') or request.GET.get('code') or ""
        to_post = {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            # 'redirect_uri': re.match('(.*)\?', request.build_absolute_uri()).group(1),
            'redirect_uri': self.get_domain(),
            'code': code
        }
        res = requests.post(
            url="https://api.instagram.com/oauth/access_token", data=to_post)
        print res,'---------------------------------------------'
        user_details = res.json()['user']
        lf = LoggedFrom.objects.get(name="instagram")
        try:
            user = ZapUser.objects.get(instagram_id=user_details['id'])
        except ZapUser.DoesNotExist:
            try:
                user = ZapUser.objects.get(username=user_details['username'])
                user.instagram_id = user_details['id']
                user.save()
            except ZapUser.DoesNotExist:
                user = ZapUser(instagram_id=user_details[
                    'id'], username=get_random_string(15), logged_from=lf)
                user.first_name = user_details['first_name'] if user_details.get('first_name') else user_details[
                    'full_name'] if user_details.get('full_name') else user_details['username'] if user_details.get(
                    'username') else ""
                user.last_name = user_details[
                    'last_name'] if user_details.get('last_name') else ""
                user.save()
                # issue_wallet_for_signup(user)
                up, c = UserProfile.objects.get_or_create(user=user)
                user.profile.profile_pic = user_details[
                    'profile_picture'] if user_details.get('profile_picture') else ""
                user.profile.save()
        if self.auth_login({'instagram_id': user_details['id']}):
            return HttpResponseRedirect("/#rp_my_profile")
        return HttpResponseRedirect("/")


class ZapReducedSignup(ZapView):
    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True

        else:
            return False

    def post(self, request, format=None):
        if request.user.is_authenticated():
            if not hasattr(request.user, 'zapuser'):
                logout(request)
                pass
            else:
                return self.send_response(1, {
                    'email': request.user.email,
                    'username': request.user.username,
                    'session_id': get_session_id(request),
                    'profile_completed': request.user.profile.profile_completed
                })
        data = request.data.copy()
        srlzr = ZapReducedSignupUserSlzr(data=data)
        if not srlzr.is_valid():
            print srlzr.errors
            return self.send_response(0, srlzr.errors)
        if data.get('referral_code'):
            if getattr(settings, "EASTER_REFERRAL", False):
                try:
                    ref = RefCode.objects.get(code=data['referral_code'])
                except (RefCode.DoesNotExist, KeyError):
                    return self.send_response(0, {'referral_code': 'Incorrect refferal code.'})

        query = srlzr.validated_data
        query['logged_from'] = LoggedFrom.objects.get(name="zapyle")
        query['logged_device'] = LoggedDevice.objects.get(
            name=data['logged_device'])
        user = ZapUser()
        print query

        full_name = query['full_name']
        name_parts = full_name.rsplit(' ', 1)
        first_name = name_parts[0]
        try:

            last_name = name_parts[1]
        except IndexError:
            last_name = ''


        user.email, user.username, user.zap_username = query['email'], query['zap_username'], query['zap_username']
        user.logged_from, user.first_name, user.last_name = query['logged_from'], first_name, last_name
        user.logged_device, user.phone_number = query['logged_device'], query['phone_number']
        user.set_password(query['password'])
        user.save()
        if data.get('referral_code'):
            if getattr(settings, "EASTER_REFERRAL", False):
                try:
                    ref = RefCode.objects.get(code=data['referral_code'])
                    if user not in ref.users.all():
                        ref.users.add(user)
                        user.issue_zap_wallet(int(settings.ZAPCASH_REFERRAL), mode='0' ,purpose="signup referral")
                except (RefCode.DoesNotExist, KeyError):
                    return self.send_response(0, {'referral_code': 'Incorrect refferal code.'})
        up, c = UserProfile.objects.get_or_create(user=user)
        if c:
            up.sex = query['sex']
            up.profile_completed = 2
            up.save()
        if self.auth_login({'email': data['email'], 'password': data['password']}):
            zapemail = ZapEmail()
            
            # html = 
            # zapemail.send_email(html['html'], html['subject'], {
            # }, settings.FROM_EMAIL, data['email'])
            
            html = settings.WELCOME_LOGIN_HTML
            html_body = render_to_string(
            html['html'], {})

            zapemail.send_email_alternative(html[
                                        'subject'], settings.FROM_EMAIL, data['email'], html_body)

            if user.logged_device.name in ["ios", "android"]:
                app_version = request.COOKIES.get('VER', None)
                create_gcm_device(data['gcm_reg_id'], user, platform=request.PLATFORM, app_version=app_version)
            return self.send_response(1, {'session_id': get_session_id(request),
                                          'profile_completed': request.user.profile.profile_completed})
        return self.send_response(1, {'email':'Account created. Please login to continue.'})


class ZapSignup(ZapView):
    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True
            # Redirect to a success page.

        else:
            return False

    def post(self, request, format=None):
        # import pdb//
        # #pdb.set_trace()
        if request.user.is_authenticated():
            if not hasattr(request.user, 'zapuser'):
                logout(request)
                pass
            else:
                return self.send_response(1, {
                    'email': request.user.email,
                    'username': request.user.username,
                    'session_id': get_session_id(request),
                    'profile_completed': request.user.profile.profile_completed
                })
        data = request.data.copy()
        srlzr = ZapSignupUserSlzr(data=data)
        if not srlzr.is_valid():
            print srlzr.errors
            return self.send_response(0, srlzr.errors)
        if data.get('referral_code'):
            if getattr(settings, "EASTER_REFERRAL", False):
                try:
                    ref = RefCode.objects.get(code=data['referral_code'])
                except (RefCode.DoesNotExist, KeyError):
                    return self.send_response(0, {'referral_code': 'Incorrect refferal code.'})
        query = srlzr.validated_data
        query['logged_from'] = LoggedFrom.objects.get(name="zapyle")
        user = ZapUser()
        query['logged_device'] = LoggedDevice.objects.get(
            name=data['logged_device'])
        print query
        user.email, user.username, user.zap_username = query[
                                                           'email'], query['zap_username'], query['zap_username']
        user.logged_from, user.first_name = query[
                                                'logged_from'], query['first_name']
        user.logged_device, user.phone_number = query[
                                                    'logged_device'], query['phone_number']
        user.set_password(query['password'])
        user.save()
        # issue_wallet_for_signup(user)
        if data.get('referral_code'):
            if getattr(settings, "EASTER_REFERRAL", False):
                try:
                    ref = RefCode.objects.get(code=data['referral_code'])
                    if user not in ref.users.all():
                        ref.users.add(user)
                        user.issue_zap_wallet(int(settings.ZAPCASH_REFERRAL), mode='0' ,purpose="signup referral")
                except (RefCode.DoesNotExist, KeyError):
                    return self.send_response(0, {'referral_code': 'Incorrect refferal code.'})
        up, c = UserProfile.objects.get_or_create(user=user)
        if c:
            up.profile_completed = 2
            up.save()
        if self.auth_login({'email': data['email'], 'password': data['password']}):
            zapemail = ZapEmail()
            # html = settings.WELCOME_LOGIN_HTML
            # zapemail.send_email(html['html'], html['subject'], {
            # }, settings.FROM_EMAIL, data['email'])

            html = settings.WELCOME_LOGIN_HTML
            html_body = render_to_string(
            html['html'], {})

            zapemail.send_email_alternative(html[
                                        'subject'], settings.FROM_EMAIL, data['email'], html_body)

            if user.logged_device.name in ["ios", "android"]:
                app_version = request.COOKIES.get('VER', None)
                create_gcm_device(data['gcm_reg_id'], user, platform=request.PLATFORM, app_version=app_version)
            return self.send_response(1, {'session_id': get_session_id(request),
                                          'profile_completed': request.user.profile.profile_completed})
        return self.send_response(0, {'email':'Account created. Please login to continue.'})


class ZapResetPassword(ZapView):
    def send_email(self, email):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        user = ZapUser.objects.get(email=email)
        uid = int_to_base36(user.id)
        token = default_token_generator.make_token(user)
        password_reset_url = "{0}://{1}/#/login/?q={2}-{3}".format(
            protocol,
            current_site.domain,
            uid,
            token
            # reverse("account_password_reset_token",
            #         kwargs=dict(uidb36=uid, token=token))
        )
        ctx = {
            "user": user.zap_username,
            "current_site": current_site,
            "password_reset_url": password_reset_url,
        }
        account_activities.send_password_reset_email([user.email], ctx)

    def post(self, request, format=None):
        data = request.data.copy()
        srlzr = ZapEmailSlzr(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        if not ZapUser.objects.filter(email=data['email']).exists():
            return self.send_response(0, "Email does not exist.")
        self.send_email(data['email'])
        return self.send_response(1, "Reset password link has been sent to {}".format(data['email']))


class ZapGetOtp(ZapView):
    # def post(self, request, mobno, format=None):
    #     data = request.data
    #     data['phone_number'] = mobno
    #     srlzr = PhoneNumWithOtpSrlzr(data=data)
    #     if not srlzr.is_valid():
    #         return self.send_response(0, srlzr.errors)
    #     try:
    #         user = ZapUser.objects.get(phone_number=mobno)
    #         if str(user.otp.otp) == str(data['otp']):
    #             return self.send_response(1, "Succefully Verified")
    #         else:
    #            return self.send_response(0, "Not match")
    #     except ZapUser.DoesNotExist:
    # return self.send_response(0, "This phone number is not registered with
    # zapyle.")

    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True
            # Redirect to a success page.

        else:
            return False

    def post(self, request, mobno, format=None):
        data = request.data.copy()
        srlzr = OTPResetPasswordSrlzr(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        try:
            otp = Otp.objects.get(user__phone_number__contains=data['phone_number'][-10:], otp=data['otp']).delete()
            user = ZapUser.objects.get(phone_number__contains=data['phone_number'][-10:])
            user.set_password(data['password'])
            user.save()
            return self.send_response(1, "Password changed successfully.")
        except Otp.DoesNotExist:
            return self.send_response(0, "OTP verification failed.")
        except ZapUser.DoesNotExist:
            return self.send_response(0, "Phone number does not exist.")
            # if self.auth_login({'email': user.email, 'password': data['password']}):
            #     if data['logged_device'] in ["ios", "android"]:
            #         gcm, c = ZAPGCMDevice.objects.get_or_create(registration_id=data['gcm_reg_id'], user=user, logged_device=LoggedDevice.objects.get(name=data['logged_device']))
            #     return self.send_response(1, {'session_id':get_session_id(request)})
            # return self.send_response(1, "Cannot login")

    def send_otp(self, mobno, otp):
        msg = settings.OTP_MSG.format(
            otp)
        sms = ZapSms()
        sms.send_sms(mobno, msg, action='forgot')

    def get(self, request, mobno, format=None):
        data = {'phone_number': mobno}
        srlzr = PhoneNumSrlzrOTP(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        try:
            user = ZapUser.objects.get(phone_number__contains=mobno[-10:])
        except ZapUser.DoesNotExist:
            return self.send_response(0, "Incorrect phone number. Please enter the number used for registration.")
        otp, c = Otp.objects.get_or_create(user=user)
        self.send_otp(mobno[-10:], otp.otp)
        return self.send_response(1, "OTP sent succefully")


class ZapPasswordResetTokenView(ZapView):
    def get_user(self, uidb36):
        try:
            uid_int = base36_to_int(uidb36)
        except ValueError:
            raise Http404()
        return get_object_or_404(get_user_model(), id=uid_int)

    def check_token(self, user, token):
        return default_token_generator.check_token(user, token)

    def get(self, request, uidb36, token, format=None):
        user = self.get_user(uidb36)
        if not self.check_token(self.get_user(uidb36), token):
            raise Http404

        # load html here
        return render(request, 'forget.html', {'download_link': 'download_link'})
        return self.send_response(1, "dddddddd")

    def change_password(self, user, password):
        user.set_password(password)
        user.save()

    def send_email(self, user):
        current_site = get_current_site(self.request)
        ctx = {
            "current_site": current_site,
            "user": user.zap_username if hasattr(user, 'zap_username') else ""
        }
        account_activities.send_password_change_email([user.email], ctx)

    def post(self, request, uidb36, token, format=None):
        user = self.get_user(uidb36)
        if not self.check_token(self.get_user(uidb36), token):
            raise Http404
        data = request.data.copy()
        srlzr = ResetPasswordSrlzr(data=data)
        if not srlzr.is_valid():
            # return render(request,'forget.html',srlzr.errors)
            return self.send_response(0, srlzr.errors)
        self.change_password(user, data['password'])
        # self.send_email(user)
        # return HttpResponseRedirect('/#/login/?q='+user.email)
        self.auth_login({'email': user.email, 'password': data['password']})
        return self.send_response(1, "Password changed successfully.")

    def auth_login(self, data):
        print data
        user = authenticate(**data)
        print user
        if user is not None:
            login(self.request, user)
            return True
            # Redirect to a success page.

        else:
            return False


class Test(ZapView):
    def get(self, request, format=None):
        return self.send_response(1, "success")


class Call(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        if check_phone_number(data['phone_number']):
            if request.GET.get('sendLink',False):
                p = int(data['phone_number'])
                full_nums = str(p)[-10:]
                if len(full_nums) >= 10:
                    sms = ZapSms()
                    sms.send_sms(full_nums,
                                 'Thank you for showing interest in Zapyle. Click on the link -  https://bnc.lt/download-zapyle-app and download the App to Discover, Sell and Buy fashion.')
                    AppLinkSms.objects.create(phone=str(p)[-10:])
            else:
                CallRequest.objects.create(phone=data['phone_number'])
            return self.send_response(1, 'success')
        else:
            return self.send_response(0, 'Enter valid phone number.')
        

# class TestimonialView(ZapView):
#     def get(self, request, format= None):
#         # import pdb; pdb.set_trace()
#         data = Testimonial.objects.order_by('?').first()
#         srlzr = TestimonialSerializer(data)
#         return self.send_response(1, srlzr.data)


def handler404(request):
    response = render(request, 'account/error_pages/404.html', {})
    response.status_code = 404
    return response


def handler500(request):
    response = render(request, 'account/error_pages/500.html', {})
    response.status_code = 500
    return response


def handler403(request):
    response = render(request, 'angularapp/403.html', {})
    response.status_code = 403
    return response


def issue_wallet_for_signup(user):
    if WebsiteLead.objects.filter(email=user.email).exists():
        user.issue_zap_wallet(500, mode='0' ,purpose="website lead signup")


def WebsiteHeaderProducts():
    print '-----------------------------'
    return {'test':'tester'}


def sitemap_xml(request):
    test_file = open(settings.BASE_DIR + '/../zap_apps/account/static/account/sitemap.xml', 'rb')
    response = HttpResponse(content=test_file)
    response['Content-Type'] = 'application/xml'
    return response


def send_plus_manifest(request):
    test_file = open(settings.BASE_DIR + '/../zap_apps/account/templates/account/sp-push-manifest.json', 'rb')
    response = HttpResponse(content=test_file)
    response['Content-Type'] = 'application/json'
    return response


def send_plus_worker(request):
    test_file = open(settings.BASE_DIR + '/../zap_apps/account/templates/account/sp-push-worker.js', 'rb')
    response = HttpResponse(content=test_file)
    response['Content-Type'] = 'application/javascript'
    return response


def robots_txt(request):
    test_file = open(settings.BASE_DIR + '/../zap_apps/account/templates/account/robots.txt', 'rb')
    response = HttpResponse(content=test_file)
    response['Content-Type'] = 'text/plain'
    return response
