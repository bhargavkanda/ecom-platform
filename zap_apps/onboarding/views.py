from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from zap_apps.zapuser.models import ZapUser, LoggedFrom, BrandTag, UserPreference, WaistSize
from zap_apps.address.models import State, Address
from zap_apps.zap_catalogue.models import Brand, Size, ApprovedProduct, Color, Style, Occasion, Category
from zap_apps.onboarding.models import Onboarding
from zap_apps.zap_catalogue.product_serializer import SizeSerializer
# from zap_apps.account.account_serializer import (FbUserSlzr, InstagramUserSlzr, AccestokenSerializar,
#     AccestokenSerializar, ZapLoginUserSlzr, ZapSignupUserSlzr)
from zap_apps.address.address_serializer import AddressSerializer
from zap_apps.onboarding.onboarding_serializer import OnboardingSerializerStepOne, OnboardingSerializerStepFour, OnboardingStartEndSrlsr, CategorySeriaizer
import json
from zap_apps.zapuser.zapuser_serializer import WaistSizeSrlzr
from django.conf import settings
from zap_apps.zap_notification.views import ZapSms, ZapEmail
from zap_apps.account.models import Otp
from zap_apps.zapuser.zapuser_serializer import PhoneNumWithOtpSrlzr
from zap_apps.referral.models import RefCode
from django.template.loader import render_to_string



class OnboardingView(ZapAuthView):

    def get(self, request, step, format=None):
        get_data = request.GET.copy()
        srlszr = OnboardingStartEndSrlsr(data=get_data)
        if not srlszr.is_valid():
            return self.send_response(0, srlszr.errors)
        if step == "2":
            if hasattr(request.user, 'fashion_detail'):
                data = [{'id': bt.id, 'tag': bt.tag}
                        for bt in request.user.fashion_detail.brand_tags.all()]
                btags = [{'id': bt.id, 'tag': bt.tag} for bt in BrandTag.objects.exclude(
                    id__in=[i['id'] for i in data])]
            else:
                btags = [{'id': bt.id, 'tag': bt.tag} for bt in BrandTag.objects.all()]
            try:
                btags[int(get_data.get('end', settings.BRAND_TAG_LIMIT))]
                flag = True
            except:
                flag = False
            return Response({'status':'success','data':btags[int(get_data.get('start', 0)):int(get_data.get('end', settings.BRAND_TAG_LIMIT))],'next':flag})
        if step == "3":
            if not any(i in get_data for i in ['start', 'end']):
                #selected_brands = [{'id':i['brand_id'],'brand':i['brand__brand']} for i in ApprovedProduct.objects.all().values('brand_id', 'brand__brand').distinct()]
                selected_brands = Brand.objects.filter(
                    brand__in=settings.SELECTED_BRANDS).values('id', 'brand')
            else:
                selected_brands = []
            #[get_data.get('start', 0): get_data.get('end', settings.BRAND_LIMIT)]
            #c = Brand.objects.filter(tags=request.user.fashion_detail.brand_tags.all()).count()
            #selected_brands = [{'id':b.id,'brand':b.brand} for b in Brand.objects.filter(tags=request.user.fashion_detail.brand_tags.all())]
            unselected_brands = [{'id': b.id, 'brand': b.brand} for b in Brand.objects.exclude(
                id__in=[i['id'] for i in selected_brands])[get_data.get('start', 0): get_data.get('end', settings.BRAND_LIMIT)]]

            return self.send_response(1, {
                'selected_brands': selected_brands,
                'unselected_brands': unselected_brands
            })
        if step == "4":
            global_size = WaistSize.objects.all()
            global_size_srlzr = WaistSizeSrlzr(global_size, many=True)
            # foot_sizes =
            cloth_sizes = Size.objects.filter(
                category_type="C").values('size', 'id').distinct()

            cloth_sizes = sorted(cloth_sizes, key=lambda x: x['id'])
            result = []

            for i in cloth_sizes:
                to_cal = [j['size'] for j in result]
                if not i['size'] in to_cal:
                    result.append(i)
            from decimal import Decimal
            foot_s = []
            for s in Size.objects.filter(category_type="FW"):
                d_str = str(Decimal(s.us_size))
                dicts = {'id':s.id,'us_size':d_str.rstrip('0').rstrip('.') if '.' in d_str else d_str}
                foot_s.append(dicts)
            return self.send_response(1,
                                      {
                                          'waist_sizes': global_size_srlzr.data,
                                          'foot_sizes':  foot_s,#Size.objects.filter(category_type="FW").values('id', 'us_size'),
                                          'cloth_sizes': result
                                      })
        return self.send_response(1, "No data")
        # obj, c = Onboarding.objects.get_or_create(user=request.user)
        # # obj.task3=True
        # # obj.save()
        # if obj.task4:
        #   data = {'current_step':5}
        #   return self.send_response(1, data)
        # if obj.task3:
        #   global_size = WaistSize.objects.all()
        #   global_size_srlzr = WaistSizeSrlzr(global_size, many=True)
        #   # foot_sizes =
        #   data = {'waist_sizes': global_size_srlzr.data,'current_step':4}
        #   return self.send_response(1, data)
        # if obj.task2:
        #   brands=[{'id':b.id,'brand':b.brand} for b in Brand.objects.filter(tags=request.user.fashion_detail.brand_tags.all())]
        #   data = {'current_step':3, 'brands':brands}
        #   return self.send_response(1, data)
        # if obj.task1:
        #   btags=[{'id':bt.id,'tag':bt.tag} for bt in BrandTag.objects.all()[0:20]]
        #   data = {'btags':btags,'current_step':2}
        #   return self.send_response(1, data)
        # else:
        #   if request.user.logged_from.name == 'zapyle':
        #       request.user.profile.profile_completed = 2
        #       request.user.profile.save()
        #       request.user.user_onboarding.task1=True
        #       request.user.user_onboarding.save()
        #       btags=[{'id':bt.id,'tag':bt.tag} for bt in BrandTag.objects.all()[0:20]]
        #       data = {'current_step':2, 'btags':btags}
        #       return self.send_response(1, data)
        #   data = {'current_step':1,'username':request.user.username, 'email':request.user.email}
        #   return self.send_response(1, data)
        # return
        # Response({'status':'success','task1':obj.task1,'task2':obj.task2,'task3':obj.task3,'task4':obj.task4})
    def send_otp(self, mobno, otp):
        msg = settings.OTP_MSG.format(
            otp)
        sms = ZapSms()
        print msg
        #sms.send_sms(mobno, msg)
    def post(self, request, step, format=None):
        obj, c = Onboarding.objects.get_or_create(user=request.user)
        data = request.data.copy()
        if step == "1":
            if request.GET.get('action') == 'otp':
                data['phone_number'] = request.user.phone_number
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
                request.user.phone_number_verified = True
                request.user.save()
                request.user.profile.profile_completed = 2
                request.user.profile.save()
                return self.send_response(1, "OTP verification succesfull.")
            else:
                srlszr = OnboardingSerializerStepOne(request.user, data=data)
                if srlszr.is_valid():
                    if data.get('referral_code'):
                        if getattr(settings, "EASTER_REFERRAL", False):
                            try:
                                ref = RefCode.objects.get(code=data['referral_code'])
                                if request.user not in ref.users.all():
                                    ref.users.add(request.user)
                                    request.user.issue_zap_wallet(int(settings.ZAPCASH_REFERRAL), mode='0', purpose="signup referral")
                            except RefCode.DoesNotExist:
                                return self.send_response(0, {'referral_code': 'Incorrect refferal code.'})                         
                    srlszr.save()
                    # Otp.objects.filter(user=request.user).delete()
                    # otp = Otp.objects.create(user=request.user)
                    # self.send_otp(request.user.phone_number[-10:], otp.otp)
                    if not request.user.profile.profile_completed == 5:

                        zapemail = ZapEmail()
                        # html = settings.WELCOME_LOGIN_HTML
                        # zapemail.send_email(html['html'], html['subject'], {
                        # }, settings.FROM_EMAIL, data['email'])

                        html = settings.WELCOME_LOGIN_HTML
                        html_body = render_to_string(
                        html['html'], {})

                        zapemail.send_email_alternative(html[
                                                    'subject'], settings.FROM_EMAIL, data['email'], html_body)
                        
                    request.user.user_onboarding.task1 = True
                    request.user.user_onboarding.save()
                    request.user.profile.profile_completed = 2
                    request.user.profile.save()
                    # btags=[{'id':bt.id,'tag':bt.tag} for bt in BrandTag.objects.all()[0:12]]
                    # return self.send_response(1, btags)
                    return self.send_response(1, "Username and email saved successfully")
                else:
                    return self.send_response(0, srlszr.errors)
        elif step == "2":
            print request.data['btags_selected'], 'request.data btags_selected'
            try:
                bt = BrandTag.objects.filter(
                    id__in=request.data['btags_selected'])
            except ValueError:
                bt = BrandTag.objects.filter(
                    id__in=json.loads(request.data['btags_selected']))
            up, c = UserPreference.objects.get_or_create(user=request.user)
            up.brand_tags.clear()
            up.brand_tags.add(*bt)
            if not request.user.profile.profile_completed == 5:
                request.user.profile.profile_completed = 3
            request.user.profile.save()
            request.user.user_onboarding.task2 = True
            request.user.user_onboarding.save()
            # brands=[{'id':b.id,'brand':b.brand} for b in Brand.objects.filter(tags=request.user.fashion_detail.brand_tags.all())]
            # print brands
            return self.send_response(1, "Brand Tags saved successfully")
        elif step == "3":
            brands = Brand.objects.filter(
                id__in=request.data['brands_selected'])
            up, c = UserPreference.objects.get_or_create(user=request.user)
            up.brands.clear()
            up.brands.add(*brands)
            if not request.user.profile.profile_completed == 5:
                request.user.profile.profile_completed = 4
            request.user.profile.save()
            request.user.user_onboarding.task3 = True
            request.user.user_onboarding.save()
            # global_size = Size.objects.all()
            # global_size_srlzr = SizeSerializer(global_size, many=True)
            return self.send_response(1, "Brands added successfully")
        elif step == "4":
            data = request.data
            obj, c = UserPreference.objects.get_or_create(user=request.user)
            srlszr = OnboardingSerializerStepFour(data=data)
            if not srlszr.is_valid():
                return self.send_response(0, srlszr.errors)
            request.user.fashion_detail.waist_size.clear()
            request.user.fashion_detail.foot_size.clear()
            request.user.fashion_detail.size.clear()
            request.user.fashion_detail.waist_size.add(
                *WaistSize.objects.filter(id__in=data.get('waist_sizes') or []))
            request.user.fashion_detail.foot_size.add(
                *Size.objects.filter(id__in=request.data.get('foot_sizes') or []))
            request.user.fashion_detail.size.add(
                *Size.objects.filter(id__in=request.data.get('cloth_sizes') or []))
            if not request.user.profile.profile_completed == 5:
                request.user.profile.profile_completed = 5
            request.user.profile.save()
            request.user.user_onboarding.task4 = True
            request.user.user_onboarding.save()
            return self.send_response(1, "success")


class GetBrandTags(ZapAuthView):

    def get(self, request, format=None):
        btags = [{'id': bt.id, 'tag': bt.tag} for bt in BrandTag.objects.all()]
        return self.send_response(1, btags)


class GetBrands(ZapAuthView):

    def get(self, request, format=None):
        brands = [{'id': b.id, 'brand': b.brand} for b in Brand.objects.filter(
            tags=request.user.fashion_detail.brand_tags.all())]
        return self.send_response(1, brands)


class GetAllBrand(ZapAuthView):

    def get(self, request, format=None):
        brands = [{'id': b.id, 'brand': b.brand} for b in Brand.objects.order_by('brand')]
        return self.send_response(1, brands)


class GetAllColors(ZapAuthView):

    def get(self, request, format=None):
        colors = [{'id': b.id, 'color': b.name, 'code': b.code}
                  for b in Color.objects.all()]
        return self.send_response(1, colors)


class GetAllStyles(ZapAuthView):

    def get(self, request, format=None):
        styles = [{'id': b.id, 'style': b.style_type}
                  for b in Style.objects.all()]
        return self.send_response(1, styles)


class GetAllOccasions(ZapAuthView):

    def get(self, request, format=None):
        occasions = [{'id': b.id, 'occasion': b.name}
                     for b in Occasion.objects.all()]
        return self.send_response(1, occasions)


class GetAllCategories(ZapAuthView):

    def get(self, request, format=None):
        cats = Category.objects.all().exclude(name='Swim Wear')
        srlzr = CategorySeriaizer(cats, many=True)
        return self.send_response(1, srlzr.data)
