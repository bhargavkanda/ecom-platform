from django.shortcuts import render
from django.conf import settings
from zap_apps.account.zapauth import (ZapView, ZapAuthView, 
    zap_login_required, zap_login_required_testimonials)
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout

from zap_apps.zap_analytics.tasks import track_impressions, track_profile
from zap_apps.zapuser.models import ZapUser, UserData, BuildNumber, City, UserProfile, AppViralityKey, WebsiteLead, Subscriber

from zap_apps.account.account_serializer import (FbUserSlzr, InstagramUserSlzr, AccestokenSerializar,
                                                 AccestokenSerializar, ZapLoginUserSlzr, ZapSignupUserSlzr, TestimonialSerializer)
from zap_apps.zapuser.zapuser_serializer import (AdmireSrlzr, UserDataSerializer, ReturnSerializerPOST,
                                                 CheckBuildNumberSlzr, LikeUnlikeSlzr, ProfileDetailsSerializer, ProfileDetailsSerializerV2, UserInfoSerializer,
                                                 CheckUsernameSrlzr, PhoneNumSrlzr, AndroidProfileDetailsSerializer, AndroidProfileDetailsSerializerV2,  DescriptionSlzr, UserSerializer,
                                                 CheckEmailNum, PhoneNumWithOtpSrlzr, OTPSrlzr, SubscriberSerializer)
from zap_apps.zap_catalogue.models import ApprovedProduct
import json
from zap_apps.order.models import Transaction, Order, Return, RETURN_REASONS, OrderTracker
from zap_apps.zap_catalogue.models import Brand
from django.utils import timezone
from datetime import timedelta
from zap_apps.order.views import get_order_status
from zap_apps.payment.models import ZapWallet
from django.db.models import Sum
import datetime
from zap_apps.zap_notification.views import ZapSms, ZapEmail
from zap_apps.payment.zap_citrus import get_saved_cards
from django.contrib.sites.shortcuts import get_current_site
from Crypto.Cipher import DES
import base64
import re
from zap_apps.account.models import Otp, Domain, Testimonial
from django.core.cache import cache
from zap_apps.extra_modules.appvirality import AppViralityApi
from zap_apps.zapuser.models import AppViralityKey
from django.template.loader import render_to_string
import pdb
from zap_apps.extra_modules.tasks import app_virality_conversion
from zap_apps.account.views import create_gcm_device
from zap_apps.order.order_serializer import  SingleOrderSerializer


ENCKEY = "ZaXcu6wp"


class Test(ZapAuthView):

    def get(self, request, format=None):
        data = request.GET.copy()
        print request.get_full_path()
        return self.send_response(1, "yeah..")


class MyLovedProducts(ZapAuthView):

    def get(self, request, format=None):
        l_products = request.user.loved_products.filter(status=1)
        track_user_product_impressions(request, l_products)
        return self.send_response(
            1, [{'id': i.id, 'image': i.images.all().order_by('id')[0].image.url_500x500,
                'original_price' : i.original_price, 'listing_price':i.listing_price,'category':i.product_category.parent.name,
                'title':i.title, 'sale': True if i.sale == '2' else False,'loved':True,
                'available': True if i.product_count.filter(quantity__gt=0) else False} for i in l_products]
        )


# Gets all the cities
class GetCities(ZapView):

    def get(self, request, format=None):
        return self.send_response(1, City.objects.all().values('id', 'name'))


class MyInfo(ZapAuthView):

    def get(self, request, format=None):
        data = {
            'email': request.user.email if hasattr(request.user, 'email') else None,
            'phone_number': request.user.phone_number if hasattr(request.user, 'phone_number') else None,
            'zap_username': request.user.zap_username if hasattr(request.user, 'zap_username') else None,
            'full_name': request.user.get_full_name(),
            'description': request.user.profile.description,
            'gender': request.user.profile.get_sex_display(),
            'locations': City.objects.all().values('id', 'name'),
            'profile_pic': request.user.profile.profile_pic,
            'selected_location_id': request.user.profile.city.id if request.user.profile.city else None,
            'dob': datetime.datetime.strptime(str(request.user.profile.dob), "%Y-%m-%d").strftime("%d-%m-%Y") if request.user.profile.dob else None,
        }
        if(request.GET.get('web')):
            data.update({'admirers' : request.user.profile.admiring.count(),
            'admiring' : request.user.aaaa.count(),
            'notifications' : request.user.notification.filter(read=False).count(),
            'wallet':request.user.get_zap_wallet,
            'profile_completed':request.user.profile.profile_completed})
        return self.send_response(1, data)

    def put(self, request, format=None):
        data = request.data.copy()
        srlzr = UserInfoSerializer(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        srlzr.save(request.user)
        return self.send_response(1, "User info updated successfully")


class MyZapCash(ZapAuthView):

    def get(self, request, format=None):
        # pdb.set_trace()
        return self.send_response(1, {'status': 'success', 'amount': int(request.user.get_zap_wallet)})


class MySavedCards(ZapAuthView):

    def get(self, request, format=None):
        try:
            data = get_saved_cards(
                settings.CITRUS_SIGNIN_ID, settings.CITRUS_SIGNIN_CLIENT_SECRET, request.user.email)
        except Exception as e:
            print e
            return self.send_response(1, {'paymentOptions': []})
        return self.send_response(1, data)


class MyDetail(ZapView):

    @method_decorator(zap_login_required_testimonials)
    def get(self, request, format=None):
        if not hasattr(request.user, 'zapuser'):
            return self.send_response(0, "You are logined as admin user")
        data = Testimonial.objects.order_by('?').first()
        srlzr = TestimonialSerializer(data)
        build_data = request.GET.copy()
        build = False
        if build_data:
            srlzr = CheckBuildNumberSlzr(data={"number":build_data['number']})
            if not srlzr.is_valid():
                return self.send_response(0, srlzr.errors)
            # print request.GET['number']
            # Domain.objects.get_or_create(domain=self.get_domain())
            # print BuildNumber.objects.filter(number__lte=int(request.GET['number']), app="ios")
            if BuildNumber.objects.filter(number__lte=int(request.GET['number']), app=request.PLATFORM.lower()):
                build = True
            else:
                previous_build = BuildNumber.objects.filter(app=request.PLATFORM.lower())[0]
                new_features = previous_build.new_features
                features = []
                for feature in new_features:
                    features.append({'title':feature.title, 'description':feature.description})
                return self.send_response(0, {"build":False, 'features':features})
        # print request.user
        # print request.COOKIES
        # cache_key = request.get_full_path()+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        # result = cache.get(cache_key)
        # if not result:
        data = {
            'user_id': request.user.id,
            'email': request.user.email if (hasattr(request.user, 'email') and request.user.email.strip()) else None,
            'phone_number': request.user.phone_number if hasattr(request.user, 'phone_number') else None,
            'zap_username': request.user.zap_username if hasattr(request.user, 'zap_username') else None,
            'profile_completed': request.user.profile.profile_completed,
            'username': request.user.username,
            'profile_pic': request.user.profile.profile_pic,
            'full_name': request.user.get_full_name(),
            'user_type': request.user.user_type.name,
            'testimonial': srlzr.data,
            'show_guest':settings.SHOW_GUEST,
            'description':request.user.profile.description,
            'dob': request.user.profile.dob,
            'gender': request.user.profile.sex
        }
        if build:
            data['build'] = True
            data['referral'] = getattr(settings, "EASTER_REFERRAL", False)


        result = data
            # cache.set(cache_key, result)  
        return self.send_response(1, result)

    @method_decorator(zap_login_required)
    def put(self, request, format=None):
        data = request.data
        print data
        srlzr = DescriptionSlzr(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        request.user.profile.description = data['description']
        request.user.profile.save()
        return self.send_response(1, "Profile description updated successfully")


class GetEmailNum(ZapAuthView):

    def get_domain(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}".format(
            protocol,
            current_site.domain
        )

    def get(self, request, format=None):
        return self.send_response(1, {
            'user_detail': {
                'email': request.user.email,
                'phone_number': request.user.phone_number,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'zap_username': request.user.zap_username,
                'current_site': self.get_domain()

            }
        })


class GetEmailAndNum(ZapAuthView):
        # sms.send_sms(mobno, msg)
    def get(self, request, format=None):

        return self.send_response(1, {
            'user_detail': {
                'email': request.user.email if hasattr(request.user, 'email') and request.user.email else None,
                'phone_number': request.user.phone_number if hasattr(request.user,
                                                                     'phone_number') and request.user.phone_number else None,
                'zap_username': request.user.zap_username if hasattr(request.user,
                                                                     'zap_username') and request.user.zap_username else None,
                'phone_number_verified': True if (
                settings.OTP_DISABLE and hasattr(request.user, 'phone_number') and request.user.phone_number) else False
            }
        })

    def send_otp(self, mobno, otp):
        msg = settings.OTP_MSG.format(
            otp)
        sms = ZapSms()
        sms.send_sms(mobno, msg)

    def post(self, request, format=None):
        print "....."
        data = request.data.copy()
        print data
        srlzr = CheckEmailNum(request.user, data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        # request.user.phone_number = str(data['phone_number'])[-10:]
        request.user.email = data['email']
        request.user.zap_username = data['zap_username']
        request.user.phone_number = data['phone_number']
        request.user.save()
        otp, c = Otp.objects.get_or_create(user=request.user)
        self.send_otp(request.user.phone_number[-10:], otp.otp)
        return self.send_response(1, "Phone number added Successfully.")


class CheckEmailMobNum(ZapAuthView):

    def get(self, request, format=None):
        non_fields = []
        if not request.user.phone_number:
            non_fields.append("phone_number")
        if not request.user.email:
            non_fields.append("email")
        if non_fields:
            return self.send_response(0, str(non_fields) + " are not filled")
        return self.send_response(1)


class AddPhone(ZapAuthView):
    def send_otp(self, mobno, otp):
        msg = settings.OTP_MSG.format(
            otp)
        sms = ZapSms()
        sms.send_sms(mobno, msg)

    def post(self, request, format=None):
        data = request.data.copy()
        srlzr = PhoneNumSrlzr(request.user, data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        request.user.phone_number = data['phone_number']
        request.user.save()
        otp, c = Otp.objects.get_or_create(user=request.user)
        self.send_otp(request.user.phone_number[-10:], otp.otp)
        return self.send_response(1, "Phone number added Successfully.")


class OTPVerify(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        srlzr = PhoneNumWithOtpSrlzr(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        try:
            otp = Otp.objects.get(user__phone_number=data['phone_number'], otp=data['otp'])
            user = ZapUser.objects.get(phone_number__contains=data['phone_number'])
        except Otp.DoesNotExist:
            return self.send_response(0, "OTP verification failed.")
        except ZapUser.DoesNotExist:
            return self.send_response(0, "Phone number does not exist.")
        user.phone_number = data['phone_number'][-10:]
        user.phone_number_verified = True
        user.save()
        return self.send_response(1, "OTP verification succesfull.")


class OTPVerify2(ZapAuthView):
    def post(self, request, format=None):
        data = request.data.copy()
        srlzr = OTPSrlzr(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        try:
            Otp.objects.get(user=request.user, otp=data['otp']).delete()
        except Otp.DoesNotExist:
            return self.send_response(0, "OTP verification failed.")
        request.user.phone_number_verified = True
        request.user.save()
        return self.send_response(1, "OTP verification succesfull.")


class Admire(ZapView):

    @method_decorator(zap_login_required)
    def post(self, request, format=None):
        data = request.data
        srlzr = AdmireSrlzr(data=data)
        if srlzr.is_valid():
            srlzr.save(request.user)
            return self.send_response(1, "action succesfully completed")
        else:
            return self.send_response(0, srlzr.errors)

    def put(self, request, format=None):
        admire_type = request.data.get('admire_type', 'admires')
        if not 'user_id' in request.data:
            return self.send_response(0, 'user_id fields required')
        if admire_type == 'admires':
            user = UserProfile.objects.get(user__id=request.data['user_id'])
            admires = user.admiring.all()
            serlzr = UserSerializer(admires,
                                    context={'current_user': request.user}, many=True)
            return self.send_response(1, serlzr.data)
        else:
            admiring = ZapUser.objects.filter(
                profile__admiring__in=[request.data['user_id']])
            serlzr = UserSerializer(admiring,
                                    context={'current_user': request.user}, many=True)
            return self.send_response(1, serlzr.data)


class UserAccountNumber(ZapAuthView):

    def decrypt(self, account_number):
        obj = DES.new(ENCKEY, DES.MODE_ECB)
        cipher_user_acc_no = base64.b64decode(account_number)
        user_acc_no_dummy = obj.decrypt(cipher_user_acc_no)
        user_acc_no = re.sub('[Z]', '', user_acc_no_dummy)
        return user_acc_no

    def encrypt(self, account_number):
        obj = DES.new(ENCKEY, DES.MODE_ECB)
        plain = account_number
        num = 16
        if len(plain) > 32:
            num = 32
        modified = plain + (num - len(plain)) * 'Z'
        ciph = obj.encrypt(modified)
        second_encp = base64.b64encode(ciph)
        return second_encp

    def get(self,  request, format=None):
        obj, c = UserData.objects.get_or_create(user=request.user)
        account_number = obj.account_number or ""
        if account_number:
            account_number = self.decrypt(account_number)
        ifsc_code = obj.ifsc_code or ""
        account_holder = obj.account_holder or ""
        return Response(
            {
            'status': 'success',
            'user_acc': account_number, 
            'ifsc_code': ifsc_code,
            'account_holder': account_holder
            }
        )

    def post(self, request, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        srlzr = UserDataSerializer(data=data)
        if not srlzr.is_valid():
            print srlzr.errors
            return self.send_response(0, srlzr.errors)
        # cipher = encrypt(ENCKEY, account_number)
        obj, c = UserData.objects.get_or_create(user=request.user)
        obj.old_account_number = obj.account_number
        obj.account_number = self.encrypt(data['account_number'])
        obj.ifsc_code = request.data['ifsc_code']
        obj.account_holder = request.data.get('account_holder')
        obj.save()
        if not c:
            zapsms = ZapSms()
            zapsms.send_sms(request.user.phone_number, settings.ACCOUNT_NUM_CHANGED_MSG)
            zapemail = ZapEmail()
            html = settings.ACCOUNT_NUMBER_CHANGE_HTML
            email_vars = {
                'user': request.user.get_full_name(),
            }
            html_body = render_to_string(
            html['html'], email_vars)

            zapemail.send_email_alternative(html[
                                'subject'], settings.FROM_EMAIL, request.user.email, html_body)

            # zapemail.send_email(html['html'], html[
            #                     'subject'], email_vars, settings.FROM_EMAIL, request.user.email)
        
        return self.send_response(1, "Account number updated succesfully.")


class UserAccountNumberByAdmin(ZapAuthView):

    def get(self,  request, pk, format=None):
        try:
            print '11111111111'
            obj = DES.new(ENCKEY, DES.MODE_ECB)
            ud = UserData.objects.filter(user_id=pk)
            if ud:
                base64_user_acc_no = ud[0].account_number
            else:
                base64_user_acc_no = ""
            cipher_user_acc_no = base64.b64decode(base64_user_acc_no)
            user_acc_no_dummy = obj.decrypt(cipher_user_acc_no)
            user_acc_no = re.sub('[Z]', '', user_acc_no_dummy)
            len_user_acc_no = len(user_acc_no)
            user_acc = user_acc_no[
                :2] + (len_user_acc_no - 4) * 'X' + user_acc_no[len_user_acc_no - 2:]
            if ud:
                print user_acc,'88888888888'
                return Response({'status': 'success', 'user_acc': user_acc_no, 'ifsc_code': ud[0].ifsc_code or ""})
            else:
                print '999999999999'
                return Response({'status': 'error', 'user_acc': "", 'ifsc_code': ""})

        except Exception as e:
            print e
            return Response({'error': e})

    def post(self, request, pk, format=None):
        try:
            data = request.data.copy()
            data['user'] = pk
            srlzr = UserDataSerializer(data=data)
            if not srlzr.is_valid():
                return self.send_response(0, srlzr.errors)
            obj = DES.new(ENCKEY, DES.MODE_ECB)
            plain = request.data['account_number']
            modified = plain + (16 - len(plain)) * 'Z'
            ciph = obj.encrypt(modified)
            second_encp = base64.b64encode(ciph)
            obj, c = UserData.objects.get_or_create(user_id=pk)
            obj.old_account_number = obj.account_number
            obj.account_number = second_encp
            obj.ifsc_code = request.data['ifsc_code']
            obj.save()
            len_user_acc_no = len(plain)    
            user = ZapUser.objects.get(id=pk)        
            if not c:
                zapemail = ZapEmail()
                html = settings.ACCOUNT_NUMBER_CHANGE_HTML
                email_vars = {
                    'user': user.get_full_name(),
                }

                html_body = render_to_string(
                html['html'], email_vars)

                zapemail.send_email_alternative(html[
                                    'subject'], settings.FROM_EMAIL, user.email, html_body)

                # zapemail.send_email(html['html'], html[
                #                     'subject'], email_vars, settings.FROM_EMAIL, user.email)
            return Response({'status': 'success'})
        except Exception as e:
            return Response({'error': e})


class CheckUsername(ZapAuthView):

    def post(self,  request, format=None):
        data = request.data.copy()
        srlzr = CheckUsernameSrlzr(data=data, context={'user': request.user})
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        return self.send_response(1, "Yeah available")


class CheckBuildNumber(ZapView):
    def get_domain(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}".format(
            protocol,
            current_site.domain
        )

    def get(self, request, format=None):
        srlzr = CheckBuildNumberSlzr(data=request.GET.copy())
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        # Domain.objects.get_or_create(domain=self.get_domain())
        if BuildNumber.objects.filter(number__lte=int(request.GET['number']), app="android"):
            return self.send_response(1, "Build Number Found")
        else:
            return self.send_response(0, "Build Number Not Found")


class CheckBuildNumberIOS(ZapView):
    def get_domain(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}".format(
            protocol,
            current_site.domain
        )

    def get(self, request, format=None):
        srlzr = CheckBuildNumberSlzr(data=request.GET.copy())
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        print request.GET['number']
        # Domain.objects.get_or_create(domain=self.get_domain())
        print BuildNumber.objects.filter(number__lte=int(request.GET['number']), app="ios")
        if BuildNumber.objects.filter(number__lte=int(request.GET['number']), app="ios"):
            return self.send_response(1, "Build Number Found")
        else:
            previous_build = BuildNumber.objects.filter(app=request.PLATFORM.lower())[0]
            new_features = previous_build.new_features
            features = []
            for feature in new_features:
                features.append({'title': feature.title, 'description': feature.description})
            return self.send_response(0, {"build": False, 'features': features})


class CheckBuildNumberIOS2(ZapView):
    def get_domain(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        return "{0}://{1}".format(
            protocol,
            current_site.domain
        )
    def get(self, request, format=None):
        srlzr = CheckBuildNumberSlzr(data=request.GET.copy())
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        # Domain.objects.get_or_create(domain=self.get_domain())
        print BuildNumber.objects.filter(number__lte=int(request.GET['number']), app="ios2")
        if BuildNumber.objects.filter(number__lte=int(request.GET['number']), app="ios2"):
            return self.send_response(1, "Build Number Found")
        else:
            previous_build = BuildNumber.objects.get(app="ios2")
            new_features = previous_build.new_features.values()
            # features = []
            # for feature in new_features:
            #     features.append({'title': feature.title, 'description': feature.description})
            return self.send_response(0, {"build": False, 'features': new_features})


class LikeUnlike(ZapAuthView):

    def post(self,  request, format=None):
        # import pdb; pdb.set_trace()
        data = request.data
        srlzr = LikeUnlikeSlzr(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        srlzr.save(request.user, ApprovedProduct.objects.get(
            id=data['product_id']))
        return self.send_response(1, "Action succesfull")


class ProfileDetails(ZapView):

    def get(self, request, pk, format=None):
        zuser = ZapUser.objects.get(id=pk)
        version = request.GET.get('version')
        if version and int(version) == 2:
            srlzr = ProfileDetailsSerializerV2(zuser, context={'current_user': request.user,
                                                             'type': request.GET.get('type', 'both')})
        else:
            srlzr = ProfileDetailsSerializer(zuser, context={'current_user': request.user,'type':request.GET.get('type','both')})

        track_profile_analytics(request, zuser.profile)
        return self.send_response(1, srlzr.data)


class AnProfileDetails(ZapView):

    def get(self, request, pk, format=None):
        try:
            zuser = ZapUser.objects.get(id=pk)
        except ZapUser.DoesNotExist:
            return self.send_response(0, 'No such user')

        version = request.GET.get('version')
        if version != '' and version != None:
            if int(version) == 2:
                srlzr = AndroidProfileDetailsSerializerV2(zuser, context={'current_user': request.user})
        else:
            srlzr = AndroidProfileDetailsSerializer(zuser, context={'current_user': request.user})
        track_profile_analytics(request, zuser.profile)
        return self.send_response(1, srlzr.data)


class MyBrandTags(ZapAuthView):

    def get(self, request, format=None):
        data = [{'id': bt.id, 'tag': bt.tag}
                for bt in request.user.fashion_detail.brand_tags.all()]
        return self.send_response(1, data)


class MyZapBrands(ZapAuthView):

    def get(self, request, format=None):
        get_data = request.GET.copy()
        selected_brands = [{'id': b.id, 'brand': b.brand}
                           for b in request.user.fashion_detail.brands.all()]
        unselected_brands = [{'id': b.id, 'brand': b.brand} for b in Brand.objects.exclude(
            id__in=[i['id'] for i in selected_brands])[get_data.get('start', 0): get_data.get('end', settings.BRAND_LIMIT)]]
        return self.send_response(1, {
            'selected_brands': selected_brands,
            'unselected_brands': unselected_brands})


class MyZapBrandsIOS(ZapAuthView):

    def get(self, request, format=None):
        get_data = request.GET.copy()
        selected_brands = [{'id': b.id, 'brand': b.brand}
                           for b in request.user.fashion_detail.brands.all()]
        unselected_brands = [{'id': b.id, 'brand': b.brand} for b in Brand.objects.exclude(
            id__in=[i['id'] for i in selected_brands])]
        return self.send_response(1, {
            'selected_brands': selected_brands,
            'unselected_brands': unselected_brands})


class MySizes(ZapAuthView):

    def get(self, request, format=None):
        size = [{'id': s.id, 'size': s.size, 'uk_size': s.uk_size, 'us_size': s.us_size,
                 'eu_size': s.eu_size} for s in request.user.fashion_detail.size.all()]
        waist_size = [{'id': s.id, 'size': s.size}
                      for s in request.user.fashion_detail.waist_size.all()]
        foot_size = [{'id': s.id, 'uk_size': s.uk_size, 'us_size': s.us_size,
                      'eu_size': s.eu_size} for s in request.user.fashion_detail.foot_size.all()]
        return self.send_response(1, [{'size': size, 'waist_size': waist_size, 'foot_size': foot_size}])


class MySales(ZapAuthView):

    def get(self, request, format=None):
        data = []
        # for trans in Transaction.objects.filter(cart__items__product__user=request.user, success=True).values_list('cart__items__product', 'paid_out'):
        for order in Order.objects.filter(product__user=request.user):
            # ap = ApprovedProduct.ap_objects.get(id=trans[0])
            data.append({'title': order.ordered_product.title,
                         'id':order.product.id,
                         'image': order.ordered_product.image.image.url_100x100,
                         'amount': order.total_price() - order.shipping_charge,
                         'payout': True if order.payout_status == 'paid_out' else False,
                         'size': order.ordered_product.size.replace('_','-'),
                         'listing_price':order.product.listing_price,
                         'original_price':order.product.original_price,
                         'order_id': order.id,})

        # products_sold = Transaction.objects.filter(cart__items__product__user=request.user,success=True).values_list('cart__items__product', flat=True)
        # data = [{'title':ap.title,'image':ap.images.all()[0].image.url_500x500,'amount':ap.listing_price,'payout':False,'size':{'size_type':ap.size_type,'uk_size':ap.size.all()[0].uk_size,'us_size':ap.size.all()[0].us_size,'eu_size':ap.size.all()[0].eu_size}} for ap in ApprovedProduct.objects.filter(id__in=products_sold)]

        return self.send_response(1, data)


class MyOrders(ZapAuthView):

    def can_return(self, order):
        return False if not order.delivery_date else True if (order.delivery_date + timedelta(hours=24)) > timezone.now() and not Return.objects.filter(order_id=order).exists() else False

    def get_size(self, order):
        size = order.transaction.cart.items.all()[0].size
        if order.product.size_type == "US":
            s = size.us_size
        elif order.product.size_type == "UK":
            s = size.uk_size
        elif order.product.size_type == "EU":
            s = size.eu_size
        else:
            s = size.uk_size
        return {'size_type': order.product.size_type or "UK", "size": s}

    def get(self, request, format=None):
        # pdb.set_trace()
        orders = Order.objects.filter(transaction__buyer=request.user)

        data = [
            {'image': order.ordered_product.image.image.url_100x100,
             'title':order.ordered_product.title,
             'id':order.product.id,
             'order_id': order.id,
             'listing_price':order.product.listing_price,
             'original_price':order.product.original_price,
             'status': get_order_status(order.id),
             'placed_at':order.placed_at.strftime('%d %b %Y'),
             'can_return': self.can_return(order),
             'size': order.ordered_product.size.replace('_','-'),
             'amount':order.final_payable_price(),
             'return_requested': Return.objects.filter(order_id=order).exists(),
             #'return_requested_time': Return.objects.get(order_id=order).requested_at if Return.objects.filter(order_id=order).exists() else None,
             'return_approved': Return.objects.get(order_id=order).approved if Return.objects.filter(order_id=order).exists() else None,
             } for order in orders]

        products = [order.product for order in orders]
        track_user_product_impressions(request, products)

        return self.send_response(1, {'data': data, 'reasons': dict(RETURN_REASONS)})

    def post(self, request, format=None):

        data = request.data.copy()
        srlzr = ReturnSerializerPOST(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        order = Order.objects.get(id=data['order_id'])
        if not self.can_return(order):
            return self.send_response(0, "Cannot return this product now.")
        try:
            r = Return.objects.get(
                order_id=order, order_id__transaction__buyer=request.user)
            return self.send_response(1, "Return request already done!")
        except Return.DoesNotExist:
            r = Return(order_id=order)

        r.consignee = order.consignor
        r.consignor = order.transaction.consignee
        r.reason = data['reason']
        # r.value = order.transaction.cart.cart_price_after_coupon
        r.save()
        order.order_status = 'return_requested'
        order.save()
        OrderTracker.objects.create(orders_id=order.id,status="return_requested")
        #Email to buyer
        zapemail = ZapEmail()
        html = settings.RETURN_REQUEST_BUYER_HTML
        
        # import pdb; #######pdb.set_trace()
        email_vars = {
            'user': request.user.get_full_name()
        }

        html_body = render_to_string(
        html['html'], email_vars)

        zapemail.send_email_alternative(html[
                            'subject'], settings.FROM_EMAIL, request.user.email, html_body)

        # zapemail.send_email(html['html'], html[
        #                     'subject'], email_vars, settings.FROM_EMAIL, request.user.email)
        html = settings.RETURN_REQUEST_SELLER_HTML
        
        # import pdb; #######pdb.set_trace()
        email_vars = {
            'user': order.consignor.user.get_full_name()
        }

        html_body = render_to_string(
        html['html'], email_vars)

        zapemail.send_email_alternative(html[
                            'subject'], settings.FROM_EMAIL, order.consignor.user.email, html_body)
        
        # zapemail.send_email(html['html'], html[
        #                     'subject'], email_vars, settings.FROM_EMAIL, order.consignor.user.email)

        srlzr = SingleOrderSerializer(order)
        # tracker_data = order.get_tracker()
        # print

        result = {}

        result['tracker'] = srlzr.data['tracker']
        result['rating'] = srlzr.data['rating']
        return self.send_response(1, result)


class GetMyZapCash(ZapAuthView):

    def get(self, request, format=None):
        

        zapwallet_used_objects = ZapWallet.objects.filter(
            user=request.user, credit=False)
        # zapcredit_used_objects = ZapCredit.objects.filter(
        #     user=request.user, credit=False)

        zapwallet_earned_objects = ZapWallet.objects.filter(
            user=request.user, credit=True)
        # zapcredit_earned_objects = ZapCredit.objects.filter(
        #     user=request.user, credit=True)
        total_used = (zapwallet_used_objects.aggregate(Sum('amount'))['amount__sum'] or 0)
        total_earned = (zapwallet_earned_objects.aggregate(Sum('amount'))['amount__sum'] or 0)
        # zapcash_used = [{'price': u.amount,
        #                  'product': u.transaction_id.cart.items.all()[0].product.title} for u in zapcash_used_objects]
        # zapcash_earned = [{'price': u.amount,
        #                    'product': u.return_id.order_id.product.title} for u in zapcash_earned_objects]
        # pdb.set_trace()
        data = {'used_details': [],
                'total_used': total_used,
                'total_earned': total_earned,
                'earned_details': [],
                'balance': {'status': 'success', 'amount': int(request.user.get_zap_wallet)}
                }
        return self.send_response(1, data)


class CreateSession(ZapAuthView):

    def get(self, request, format=None):
        data = request.GET.copy()
        print data
        # pdb.set_trace()
        app_version = request.COOKIES.get('VER', None)

        if 'gcm_reg_id' in data:
            create_gcm_device(data['gcm_reg_id'], request.user, platform=request.PLATFORM, app_version=app_version)
        request.user.create_zapsession()
        return self.send_response(1,"Successfully created session.")


class AppViralityKeyView(ZapAuthView):

    def post(self, request, format=None):
        data = request.data.copy()
        print data,"LLLL"
        if not 'user_key' in data:
            return self.send_response(0,"No user_key is present.")
        app, c = AppViralityKey.objects.get_or_create(user=request.user)
        app.key = data['user_key']
        app.save()
        from zap_apps.extra_modules.tasks import mixpanel_task
        if settings.CELERY_USE:
            mixpanel_task.delay(request.user.id, "Session Started", "Login")
        else:
            mixpanel_task(request.user.id, "Session Started", "Login")

        if settings.APPVIRALITY_ENABLE:
            if settings.CELERY_USE:
                app_virality_conversion.delay(request.user.id, "ZapSignup", "ZapSignup")
            else:
                app_virality_conversion(request.user.id, "ZapSignup", "ZapSignup")
        return self.send_response(1,"Successfully added user_key.")


class ZapCashView(ZapAuthView):
    def get(self, request, format=None):
        zapcash_used_objects = ZapWallet.objects.filter(
            user=request.user, credit=False)
        zapcash_earned_objects = ZapWallet.objects.filter(
            user=request.user, credit=True)
        balance = (zapcash_earned_objects.aggregate(Sum('amount'))['amount__sum'] or 0) - (zapcash_used_objects.aggregate(Sum('amount'))['amount__sum'] or 0)
        return self.send_response(1, {'zapcash': balance})


# class ZapCreditView(ZapAuthView):
#     def get(self, request, format=None):
#         zapcredit_used_objects = ZapCredit.objects.filter(
#             user=request.user, credit=False)
#         zapcredit_earned_objects = ZapCredit.objects.filter(
#             user=request.user, credit=True)

#         balance = (zapcredit_earned_objects.aggregate(Sum('amount'))['amount__sum'] or 0) - (zapcredit_used_objects.aggregate(Sum('amount'))['amount__sum'] or 0)
#         return self.send_response(1, {'zapcredit': balance})
def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class WebsiteLeads(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        if not validateEmail(data['email']):
            return self.send_response(0, 'invalid email')
        if ZapUser.objects.filter(email=data['email']).exists():
            return self.send_response(0, 'zapuser')
        obj, created = WebsiteLead.objects.get_or_create(email=data['email'])
        if not created:
            return self.send_response(0, 'credited already')
        return self.send_response(1, 'registered')


def get_profile_analytics_data(request, profile):
    platform = request.PLATFORM
    user = request.user
    profile_data = {
        'profile': profile,
        'platform': platform,
        'user': user
    }
    return profile_data


def track_profile_analytics(request, profile):
    if request.PLATFORM is None:
        print('Cannot track platform analytics! Platform not defined!')
        return
    profile_analytics_data = get_profile_analytics_data(request, profile)
    if settings.CELERY_USE:
        track_profile.delay(profile_analytics_data)
    else:
        track_profile(profile_analytics_data)


def track_user_product_impressions(request, products):
    if request.PLATFORM is None:
        return
    if settings.CELERY_USE:
        track_impressions.delay([product.id for product in products], 1, request.PLATFORM, 'F', request.user)
    else:
        track_impressions([product.id for product in products], 1, request.PLATFORM, 'F', request.user)


class Subscribe(ZapView):

    def post(self, request, id, format=None):
        post_data = request.data.copy()
        if id:
            try:
                subscriber = Subscriber.objects.get(id=id)
                srlzr = SubscriberSerializer(subscriber, data=post_data)
                s = srlzr.save()
                return self.send_response(1, {'id': s.id})
            except Exception:
                return self.send_response(0, 'Sorry! Subscriber does not exist.')
        else:
            srlzr = SubscriberSerializer(data = post_data)
            if srlzr.is_valid():
                s = srlzr.save()
                return self.send_response(1, {'id':s.id})
            else:
                return self.send_response(0, srlzr.errors())



class BranchAppInstallHook(ZapView):

    def post(self, request, format=None):
        json = request.data.copy()
        data = str(request.data.copy())
        referral_user = json['session_referring_link_data']['data']['referral_user_id']

        referral_wallet = ZapWallet()
        referral_wallet.user = ZapUser.objects.get(id=referral_user)
        referral_wallet.amount = 100
        referral_wallet.mode = 0
        referral_wallet.purpose = 'Friend installed app'
        referral_wallet.credit = True
        referral_wallet.save()

        # from zap_apps.zapuser.models import BranchTest
        # b = BranchTest()
        # b.content = data
        # b.source = 'install'
        # b.save()


class BranchSignupHook(ZapView):

    def post(self, request, format=None):
        data = str(request.data.copy())
        from zap_apps.zapuser.models import BranchTest
        b = BranchTest()
        b.content = data
        b.source = 'hook'
        b.save()

        json = request.data.copy()
        referral_user = json['metadata']['referral_user_id']
        friend = json['metadata']['friend_user_id']

        referral_wallet = ZapWallet()
        referral_wallet.user = ZapUser.objects.get(id=int(referral_user))
        referral_wallet.amount = 100
        referral_wallet.mode = 0
        referral_wallet.purpose = 'Friend installed app'
        referral_wallet.credit = True
        referral_wallet.save()

        friend_wallet = ZapWallet()
        friend_wallet.user = ZapUser.objects.get(id=int(friend))
        friend_wallet.amount = 100
        friend_wallet.mode = 0
        friend_wallet.purpose = 'Got referred by a friend'
        friend_wallet.credit = True
        friend_wallet.save()
