# encoding=utf8
from django.conf import settings
from django.db.models import Q, F
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from rest_framework.response import Response
from zap_apps.account.zapauth import admin_only
from zap_apps.order.models import Return, Transaction, OrderTracker
from zap_apps.zap_catalogue.models import NumberOfProducts, Size, Occasion, Color, SubCategory, Style, AGE, CONDITIONS, \
    SALE_CHOICES, Category, Brand
from zap_apps.zap_admin.admin_serializer import *
from zap_apps.zap_catalogue.product_serializer import ApprovedProductSerializer as ApprovedProductSerializerFOREXPORT
from zap_apps.zapuser.models import ZAPGCMDevice, UserProfile, BrandTag, UserPreference, ZapSession
from zap_apps.zap_notification.views import ZapSms, ZapEmail
from zap_apps.zap_catalogue.product_serializer import (AndroidSingleApprovedProducSerializer,
                                                       ApprovedProductSerializerAndroid,
                                                       ProductImageSerializer, ProductsToApproveSerializer,
                                                       NumberOfProductSrlzr, StateSerializer,
                                                       GetCategorySerializer, SubCategorySerializer, SizeSerializer,
                                                       BrandSerializer, OccasionSerializer,
                                                       ColorSerializer, StyleSerializer)
from Crypto.Cipher import DES
from zap_apps.logistics.models import Logistics, LogisticsLog, LOGISTICS_PARTNERS
from django.db.models import Count, Max, Sum
from zap_apps.address.models import State

ENCKEY = "ZaXcu6wp"
import base64
import re
import requests
import datetime
from zap_apps.logistics.logistics_serializer import LogisticsSerializer
# from zap_apps.logistics.tasks import parcelled_pickup_check
from django.core.cache import cache
from django.utils import timesince, timezone
from datetime import date, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import signals
from zap_apps.zap_notification.tasks import zaplogging
from django.db import IntegrityError
from zap_apps.zap_notification.views import ZapEmail, PushNotification, ZapSms
from zap_apps.zap_notification.models import Notification
from zap_apps.zap_catalogue.tasks import send_to_tornado
from zap_apps.marketing.models import ClosetCleanup
from zap_apps.extra_modules.tasks import app_virality_conversion
import csv
from django.http import HttpResponse, HttpResponseRedirect
from zap_apps.marketing.models import ClosetCleanup
from django import forms
# from zap_apps.zap_admin.models import MarketingImage
import ast
from zap_apps.marketing.tasks import marketing_send_notif
from zap_apps.zap_notification.views import get_json_for_push_notification, clevertap_push_notification
from zap_apps.zap_catalogue.product_serializer import GetApprovedProductSerializer
import json
from zap_apps.marketing.models import Action
from zap_apps.address.address_serializer import GetAddressSerializer, AddressSerializer
from zap_apps.address.models import Address
from operator import itemgetter
from zap_apps.logistics.tasks import logistics_evaluator, pickup_orders_logistics, pickup_update, payouts, \
    pickup_returns_logistics, update_order_status, rejected_products, track_order
from zap_apps.logistics.tasks import decryptAcc
from zap_apps.zapuser.models import UserData
from zap_apps.zapuser.zapuser_serializer import UserDataSerializer
from django.db.models import Count
from django.db.models import CharField, Case, Value, When, IntegerField
from django.contrib.sites.shortcuts import get_current_site
from zap_apps.cart.models import Cart
from collections import Counter

pushnots = PushNotification()

def parcelled_pickup_check(pincodes):
    pincodes = set(filter(None, pincodes))
    if not pincodes:
        pincodes = [u'560003']
    # print pincodes
    pincodes_str = ",".join(filter(None, pincodes))
    url = settings.PARCELLED_BASE_URL + 'pickup_serviceability/' + pincodes_str
    headers = {'parcelled-api-key': settings.PARCELLED_API_KEY, 'Content-Type': 'application/json'}
    resp = requests.get(url, headers=headers)
    json_response = resp.json()
    return json_response


@api_view(['GET', 'POST', ])
@admin_only
def home(request):
    return render(request, 'admin/zapadmin.html', {'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})


@api_view(['GET', 'POST', ])
@admin_only
def editProduct(request, p_id=None, action=None):
    return render(request, 'admin/editproduct.html',
                  {'p_id': p_id, 'action': action, 'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})


@api_view(['GET', 'POST', ])
@admin_only
def user_profile(request, p_id=None):
    user = ZapUser.objects.get(id=p_id)
    serlzr = UserProfileSerializer(user)
    return render(request, 'admin/user_profile.html', serlzr.data)
@api_view(['GET', 'POST', ])
@admin_only
def user_search(request, query_string):
    Q1 = Q(zap_username__istartswith=query_string, email__isnull=False)
    Q2 = Q(email__istartswith=query_string, zap_username__isnull=False)
    data = [{'text':u.zap_username+' ('+u.email+')','id':[u.id,u.user_type.name]} for u in ZapUser.objects.filter(Q1 | Q2)]#, email__isnull=False)]
    return Response({'results':data})

@api_view(['GET', 'POST', ])
@admin_only
def product_search(request, query_string):
    data = [{'text':'{} (id : {})'.format(p.title,p.id),'id':[p.id,p.title]} for p in ApprovedProduct.ap_objects.filter(title__icontains=query_string)]
    return Response({'results':data})



@api_view(['GET', 'POST', ])
@admin_only
def get_productsToApprove(request, page):
    cache_key = request.get_full_path()
    result = cache.get(cache_key)
    if not result:
        search_word = request.GET.get('search_word', '')
        if not search_word:
            products = ApprovedProduct.pta_objects.order_by('-upload_time','-update_time')
        else:
            products = ApprovedProduct.pta_objects.filter(Q(title__icontains=search_word)|Q(user__zap_username__icontains=search_word)).order_by('-upload_time','-update_time')
        current_page = request.GET.get('page', 1)
        perpage = request.GET.get('perpage', 10)
        paginator = Paginator(products, perpage)

        if page:
            page = int(page)
        if not paginator.num_pages >= page or page == 0:
            data = {
                'data': [],
                'page': current_page,
                'total_pages': paginator.num_pages,
                'next': True if page == 0 else False,
                'previous': False if page == 0 else True}
            return Response(data)
        p = paginator.page(page)
        if products:
            if settings.PARCEL_CHECK_ENABLED:
                parcel_data = parcelled_pickup_check(products.values_list('pickup_address__pincode', flat=True))
            else:
                parcel_data = {}
                parcel_data['data'] = []
        srlzr = ApprovedProductsSerializer(p, many=True, context={'parcel_data': parcel_data['data'] if p else []})
        data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}
        result = data
        cache.set(cache_key, result)
    return Response(result)

@api_view(['GET', 'POST'])
def closet_cleanup(request):
    if request.method == 'POST':
        data = request.data.copy()
        srlzr = LandingPageSrlzr(data=data)
        if not srlzr.is_valid():
            return render(request, 'landing/closet-cleanup.html', {'errors': srlzr.errors, 'data': data})
        data = {i:j for i,j in data.items()}
        ClosetCleanup.objects.create(**data)
        return HttpResponseRedirect('?success=true')
    else:
        return render(request, 'landing/closet-cleanup.html')

@api_view(['GET', 'POST'])
def get_free_tory_burch(request):
    if request.method == 'POST':
        # data = request.data.copy()
        # srlzr = LandingPageSrlzr(data=data)
        # if not srlzr.is_valid():
        #     return render(request, 'landing/closet-cleanup.html', {'errors': srlzr.errors, 'data': data})
        # data = {i:j for i,j in data.items()}
        # ClosetCleanup.objects.create(**data)
        return HttpResponseRedirect('?success=true')
    else:
        return render(request, 'landing/closet-cleanup3.html')
@api_view(['GET', 'POST'])
def closet_cleanup2(request):
    if request.method == 'POST':
        data = request.data.copy()
        srlzr = LandingPageSrlzr2(data=data)
        if not srlzr.is_valid():
            return render(request, 'landing/closet-cleanup2.html', {'errors': srlzr.errors, 'data': data})
        data = {i:j for i,j in data.items()}
        ClosetCleanup.objects.create(**data)
        return HttpResponseRedirect('?success=true')
    else:
        return render(request, 'landing/closet-cleanup2.html')
@api_view(['GET'])
@admin_only
def get_approvedProducts(request, page):
    cache_key = request.get_full_path()
    result = cache.get(cache_key)
    if not result or 1:
        search_word = request.GET.get('search_word', '')
        if not search_word:
            products = ApprovedProduct.ap_objects.all().order_by('-update_time')
        else:
            products = ApprovedProduct.ap_objects.filter(Q(title__icontains=search_word) | Q(user__zap_username__icontains=search_word))
        current_page = request.GET.get('page', 1)
        perpage = request.GET.get('perpage', 10)
        paginator = Paginator(products, perpage)

        if page:
            page = int(page)
        if not paginator.num_pages >= page or page == 0:
            data = {
                'data': [],
                'page': current_page,
                'total_pages': paginator.num_pages,
                'next': True if page == 0 else False,
                'previous': False if page == 0 else True}
            return Response(data)
        p = paginator.page(page)
        serlzr = ApprovedProductsSerializer(p, many=True)
        data = {'data': serlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}
        result = data
        cache.set(cache_key, result)
    return Response(result)
    
@api_view(['GET', 'POST'])
def get_free_tory_burch(request):
    if request.method == 'POST':
        # data = request.data.copy()
        # srlzr = LandingPageSrlzr(data=data)
        # if not srlzr.is_valid():
        #     return render(request, 'landing/closet-cleanup.html', {'errors': srlzr.errors, 'data': data})
        # data = {i:j for i,j in data.items()}
        # ClosetCleanup.objects.create(**data)
        return HttpResponseRedirect('?success=true')
    else:
        return render(request, 'landing/closet-cleanup3.html')

@api_view(['GET', 'POST', ])
@admin_only
def get_DisapprovedProducts(request, page):
    cache_key = request.get_full_path()
    result = cache.get(cache_key)
    if not result:
        search_word = request.GET.get('search_word', '')
        if not search_word:
            products = ApprovedProduct.dp_objects.all()
            #products = ApprovedProduct.dp_objects.all().order_by('-id')
        else:
            products = ApprovedProduct.dp_objects.filter(Q(title__icontains=search_word)|Q(user__zap_username__icontains=search_word))
            #products = ApprovedProduct.dp_objects.filter(Q(title__icontains=search_word)|Q(user__zap_username__icontains=search_word))

        current_page = request.GET.get('page', 1)
        perpage = request.GET.get('perpage', 10)
        paginator = Paginator(products, perpage)

        if page:
            page = int(page)
        if not paginator.num_pages >= page or page == 0:
            data = {
                'data': [],
                'page': current_page,
                'total_pages': paginator.num_pages,
                'next': True if page == 0 else False,
                'previous': False if page == 0 else True}
            return Response(data)
        p = paginator.page(page)
        if products:
            if settings.PARCEL_CHECK_ENABLED:
                parcel_data = parcelled_pickup_check(products.values_list('pickup_address__pincode',flat=True))
            else:
                parcel_data = {}
                parcel_data['data'] = []
        serlzr = ApprovedProductsSerializer(p, many=True,context={'parcel_data': parcel_data['data'] if p else []})
        #serlzr = DisapprovedProductsSerializer(p, many=True,context={'parcel_data': parcel_data['data'] if products else []})

        data = {'data': serlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}
        result = data
        cache.set(cache_key, result)
    return Response(result)


@api_view(['GET', 'POST', ])
@admin_only
def Product(request, p_id):
    product = ApprovedProduct.objects.filter(id=p_id)[0:15]
    serlzr = ApprovedProductsSerializer(product)
    return Response(serlzr.data)


@api_view(['GET', 'POST', 'DELETE'])
@admin_only
def Approve(request, p_id):
    if request.method == 'POST':

        p_id = request.data['product']
        p = ApprovedProduct.objects.get(id=p_id)
        print p
        if p.completed == True:
            p.status = '1'
            p.update_time = timezone.now()
            p.save()

            zapemail = ZapEmail()
            html = settings.PRODUCT_APPROVED_HTML
            # import pdb; #####pdb.set_trace()
            email_vars = {
                'album_user': p.user.get_full_name(),
                'album_name': p.title
            }

            html_body = render_to_string(
                html['html'], email_vars)

            zapemail.send_email_alternative(html[
                                                'subject'], settings.FROM_EMAIL, p.user.email, html_body)

            # zapemail.send_email(html['html'], html[
            #                         'subject'], email_vars, settings.FROM_EMAIL, p.user.email)
            instance = p
            msg = "Your product - " + \
                (instance.title or "") + " has been approved by Zapyle."
            pushnots.send_notification(instance.user, msg)
            Notification.objects.create(
                user=instance.user, message=msg, product=instance, action="ap")
            zapsms = ZapSms()
            zapsms.send_sms(instance.user.phone_number, settings.LIST_APPROVED_MSG)
            if settings.APPVIRALITY_ENABLE:
                if settings.CELERY_USE:
                    app_virality_conversion.delay(instance.user.id, "BuyOrSell", "Sell")
                else:
                    app_virality_conversion(instance.user.id, "BuyOrSell", "Sell")
            if getattr(settings, "TORNADO_USE", False):
                try:
                    if settings.CELERY_USE:
                        send_to_tornado.delay(instance.id, instance.user.id)
                    else:
                        send_to_tornado(instance.id, instance.user.id)
                except:
                    pass
            return Response({'status': 'success', 'data': 'approvedSrlzr.data'})
            #return Response({'status': 'success', 'data': approvedSrlzr.data})
        else:
            return Response({'status': 'error', 'data': 'approvedSrlzr.errors'})
            #return Response({'status': 'error', 'data': approvedSrlzr.errors})
    if request.method == 'DELETE':
        try:
            product = ApprovedProduct.objects.get(id=p_id)
        except ApprovedProduct.DoesNotExist:
            return Response({'status': 'no permission'})
        if product.product_count.filter(quantity=0):
        # if product.ordered_product.count() > 0:
            return Response({'status': 'error', 'detail': 'Product is soldout, make quantity to 1 for force delete!'})
        product.status = '3'
        product.save()
        # approvedSrlzr = GetApprovedProductSerializer(product)
        # deltdSrlze = DeletedProductSerializer(data=approvedSrlzr.data)
        # if deltdSrlze.is_valid():
        #     deltdProduct = deltdSrlze.save()
        #     n_o_p = NumberOfProducts.objects.filter(product=p_id).update(
        #         product=None, deleted_product=deltdProduct.id)
        #     product.delete()
        # else:
        #     print 'not is_valid', deltdSrlze.errors
        return Response({'status': 'success'})


@api_view(['GET', 'POST', 'DELETE'])
@admin_only
def Reject(request, p_id):
    if request.method == 'POST':
        # if request.GET.get('action') == 'approved':
        #     product = ApprovedProduct.objects.get(id=p_id)
        #     if not product.ordered_product.count() == 0:
        #         return Response({'status':'error','detail':'This product is sold out'})
        #     serlzr = ApprovedProductSerializer(product)
        # else:
        #     product = ApprovedProduct.pta_objects.get(id=p_id)
        #     serlzr = GetProductsToApproveSerializer(product)
        # datas = serlzr.data
        # datas['disapproved_reason'] = request.data['reason']
        # rejectedSrlzr = RejectedProductSerializer(data=datas)
        # if rejectedSrlzr.is_valid():
        try:
            product = ApprovedProduct.objects.get(id=p_id)
        except ApprovedProduct.DoesNotExist:
            return Response({'status': 'error', 'data': 'rejectedSrlzr.errors'})
        product.disapproved_reason = request.data['reason']
        product.status = '2'
        product.update_time = timezone.now()
        product.save()
        instance = product
        if request.data.get('send_pushnot') == True:
            msg = "Your product - " + \
                (instance.title or "") + " has been disapproved by Zapyle(" + \
                instance.get_disapproved_reason_display() + ")."
            # pushnots.send_notification(instance.user, msg)
            pushnots.send_notification(instance.user, msg, extra={'action': 'disapproved', 'msg': msg, 'marketing': '1'})
            Notification.objects.create(message=msg)
        return Response({'status': 'success', 'data': 'rejectedSrlzr.data'})
        # else:
        #     return Response({'status': 'error', 'data': 'rejectedSrlzr.errors'})

    if request.method == 'DELETE':
        try:
            product = ApprovedProduct.objects.get(id=p_id)
        except ApprovedProduct.DoesNotExist:
            return Response({'status': 'error'})
        if product.product.count() > 0:
            return Response({'status': 'error'})
        product.status = '3'
        product.update_time = timezone.now()
        product.save()
        # n_o_p = NumberOfProducts.objects.filter(
        #     Q(product=p_id) | Q(product_to_approve=p_id) | Q(disapproved_product=p_id)).update(
        #     product=None, product_to_approve=None, disapproved_product=None, deleted_product=product.id)
        return Response({'status': 'success'})
        # try:
        #     p = ApprovedProduct.objects.get(id=p_id)
        #     p.status = '3'
        #     p.save()
        #     return Response({'status': 'success'})
        # except ApprovedProduct.DoesNotExist:
        #     return Response({'status': 'error'})


@api_view(['GET', 'POST', ])
@admin_only
def get_userDetails(request):
    search_word = request.GET.get('search_word')
    if search_word and not search_word=='undefined':
        users = ZapUser.objects.filter(Q(zap_username__icontains=search_word) | Q(email__icontains=search_word) | Q(phone_number__icontains=search_word))[0:30]
    else:
        users = ZapUser.objects.all()[0:30]
    srlzr = ZapUserDetailsSerializer(users, many=True)
    return Response({'status': 'success', 'data': srlzr.data})



@api_view(['GET', 'POST', 'PUT'])
@admin_only
def get_orders(request):
    if request.method == 'GET':
        orders = Order.objects.order_by('-id')
        current_page = int(request.GET.get('page', 1))
        page = current_page
        perpage = request.GET.get('perpage', 20)
        paginator = Paginator(orders, perpage)
        p = paginator.page(page)
        srlzr = OrderSerializer(p, many=True)
        data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}


        return Response({'status': 'success', 'data': data})

    elif request.method == 'PUT':
        data = request.data.copy()
        if 'pick_id' in data:
            order = Order.objects.get(id=data['order_id'])
            if data['type'] == 'seller':
                order.consignor_id = data['pick_id']
            else:
                order.consignee_id = data['pick_id']
            order.save()
            return Response({'status': 'success'})
        try:
            order = Order.objects.get(id=data['order_id'])
        except Order.DoesNotExist:
            return Response({'status': 'error'})
        if data['c_type'] == 'seller':
            order.confirmed_with_seller = True
        else:
            order.confirmed_with_buyer = True
        order.save()
        if order.confirmed_with_seller and order.confirmed_with_buyer:
            order.order_status = 'confirmed'
            order.save()
            OrderTracker.objects.create(orders_id=order.id,status="confirmed")
            return Response({'status': 'success','message' : 'confirmed'})
        return Response({'status': 'success','message':''})
    elif request.method == 'POST':
        data = request.data.copy()
        orders = Order.objects.filter(order_number=data['order_id'])
        current_page = 1
        page = 1
        perpage = request.GET.get('perpage', 1)
        paginator = Paginator(orders, perpage)
        p = paginator.page(page)
        srlzr = OrderSerializer(p, many=True)
        data = {'data': srlzr.data, 'page': 1, 'total_pages': 1,
                'next': False, 'previous': False}
        if orders:
            return Response({'status': 'success', 'data': data})
        else:
            return Response({'status' : 'error'})



@api_view(['GET', 'POST', 'PUT'])
@admin_only
def get_admin_orders(request):
    if request.method == 'GET':
        orders = Order.objects.filter(product__isnull=False).exclude(order_status__in=['on_hold', 'failed']).order_by('-id')[0:30]
        srlzr = AdminOrderSerializer(orders, many=True)
        return Response({'status': 'success', 'data': srlzr.data})


@api_view(['GET', 'POST', ])
@admin_only
def NotifyUsers(request):
    users = ZapUser.objects.filter(zap_username__isnull=False).order_by('zap_username')
    data = [{'id': u.id, 'name': u.zap_username} for u in users]
    gcmUsers = [{'id': u.user.id, 'name': u.user.zapuser.zap_username}
                for u in ZAPGCMDevice.objects.all()]
    with open(settings.BASE_DIR + '/settings/marketing.json') as mar:
        marketing_actions = json.loads(mar.read())['actions']
    actions = []#[{'action_type': a.action_type,'data':a.data} for a in Action.objects.all()]
    return Response({'status': 'success', 'users': data,
                     'push_not_users': gcmUsers,
                     'actions':actions,
                     'marketing_actions': marketing_actions})


@api_view(['GET', 'POST', ])
@admin_only
def GetReturns(request):
    if request.method == 'GET':
        returns = Return.objects.order_by('-id')[0:30]
        serlzr = ReturnSerializer(returns, many=True)
        return Response({'status': 'success', 'data': serlzr.data})
    elif request.method == 'POST':
        data = request.data.copy()
        try:
            returnOject = Return.objects.get(id=data['id'])
        except Return.DoesNotExist:
            return Response({'status': 'error'})
        returnOject.approved = True
        returnOject.save()
        return Response({'status': 'success'})


@api_view(['POST', ])
@admin_only
def UploadImage(request):
    data = request.data.copy()
    img_serializer = ProductImageSerializer(data={'image': data['img_url']})
    if img_serializer.is_valid():
        while True:
            try:
                img_serializer.save()
                break
            except IntegrityError:
                pass
        return Response({'status': 'success', 'img_id': {'pos': data['pos'], 'id': img_serializer.data['id']}})
    else:
        return Response({'status': 'error', 'detail': img_serializer.errors})


@api_view(['POST', 'PUT'])
@admin_only
def UploadProduct(request):
    if request.method == 'POST':
        # data2 = request.data.copy()
        # data2.pop('images')
        # print data2
        data = request.data.copy()
        user = ZapUser.objects.get(id=data['user'])
        if user.user_type.name in ['zap_exclusive', 'zap_dummy']:
            data['with_zapyle'] = True
        data['user'] = user
        # image_list = request.data['images']
        # img_ids = []
        # for i in image_list:
        #     img_serializer = ProductImageSerializer(
        #         data={'image': i['img_url']})
        #     if img_serializer.is_valid():
        #         img_serializer.save()
        #         img_ids.append(img_serializer.data['id'])
        #     else:
        #         return Response({'status': 'error', 'detail': serializer.errors})
        # data['images'] = img_ids
        # data['images'] = [data['images']]
        sorted_ids = [i['id'] for i in sorted(data['images'], key=itemgetter('pos'))]
        img_ids = list(sorted_ids)
        sorted_ids.sort()
        if sorted_ids == img_ids:
            data['images'] = sorted_ids
        else:
            data['images'] = []
            for id in img_ids:
                img = ProductImage.objects.get(id=id)
                img.pk = None
                while True:
                    try:
                        img.save()
                        break
                    except IntegrityError:
                        pass
                data['images'].append(img.id)
            ProductImage.objects.filter(id__in=img_ids).delete()
        if 'original_price' in data:
            data['discount'] = (float(data['original_price']) - float(
                data['listing_price'])) / float(data['original_price'])
        if data.get('global_size') == "Free Size":
            data['size_type'] = 'FREESIZE'
        data['completed'] = True
        serlzr = ApprovedProductSerializer(data=data)
        if serlzr.is_valid():
            words = re.findall('#\S', data['description'])
            if words:
                for i in words:
                    Hashtag.objects.get_or_create(tag=i)
            p_t_a = serlzr.save()
            if data.get('global_size') == "Free Size":
                data_to_numofproducts = {
                    'size': Size.objects.get(category_type="FS").id,
                    'product': p_t_a.id,
                    'quantity': data.get('free_quantity', 1)}
                p_t_a_srlzr = NumberOfProductSrlzr(data=data_to_numofproducts)
                if p_t_a_srlzr.is_valid():
                    p_t_a_srlzr.save()
            else:
                for size_selected in request.data['global_size']:
                    size_selected['product'] = p_t_a.id
                    p_t_a_srlzr = NumberOfProductSrlzr(data=size_selected)
                    if p_t_a_srlzr.is_valid():
                        p_t_a_srlzr.save()
            if user.user_type.name == 'zap_exclusive' and data['sale'] == '2':
                zap_exc, c = ZapExclusiveUserData.objects.get_or_create(email=data['email'])
                data['products'] = [p_t_a.id] + list(zap_exc.products_to_approve.all().values_list('id',flat=True))
                zapexc = ZapExclusiveUserDataSerializer(zap_exc, data=data,partial=True)

                if zapexc.is_valid():
                    print 'zapexc saved'
                    zapexc.save()
                else:
                    return Response({'status': 'success', 'detail': zapexc.errors})
            zapemail = ZapEmail()
            internal_html = settings.UPLOAD_ALBUM_INTERNAL_HTML

            html = settings.UPLOAD_ALBUM_HTML

            internal_email_vars = {
                'user': user.get_full_name(),
                'type': p_t_a.get_sale_display(),
                'album_name': p_t_a.title
            }

            internal_html_body = render_to_string(
                internal_html['html'], internal_email_vars)

            zapemail.send_email_alternative(internal_html[
                                                'subject'], settings.FROM_EMAIL, "zapyle@googlegroups.com",
                                            internal_html_body)

            # zapemail.send_email(internal_html['html'], internal_html[
            #                     'subject'], email_vars, settings.FROM_EMAIL, "zapyle@googlegroups.com")
            email_vars = {
                'user': user.get_full_name()
            }

            html_body = render_to_string(
                html['html'], email_vars)

            zapemail.send_email_alternative(html[
                                                'subject'], settings.FROM_EMAIL, user.email, html_body)

            # zapemail.send_email(html['html'], html[
            #                     'subject'], email_vars, settings.FROM_EMAIL, user.email)
            return Response({'status': 'success', 'data': serlzr.data})
        return Response({'status': 'error', 'detail': serlzr.errors})
    elif request.method == 'PUT':
        return Response({'status': 'success'})
        # data = request.data.copy()
        # print request.data,'---0)))'
        # if data['sale'] == '1':   
        #     serlzr = SocialProductSerializer(data=data)
        # else:          
        #     serlzr = SaleProductSerializer(data=data)
        # if serlzr.is_valid():
        #     if ZapUser.objects.filter(id=data['user'],user_type__name='zap_exclusive').exists() and not data.get('email',''):
        #         return Response({'status':'error','detail':"Select Seller Account"})
        #     return Response({'status':'success'})
        # else:
        #     return Response({'status':'error','detail':serlzr.errors})


@api_view(['GET', 'POST'])
def closet_cleanup(request):
    if request.method == 'POST':
        data = request.data.copy()
        srlzr = LandingPageSrlzr(data=data)
        if not srlzr.is_valid():
            return render(request, 'landing/closet-cleanup.html', {'errors': srlzr.errors, 'data': data})
        data = {i:j for i,j in data.items()}
        ClosetCleanup.objects.create(**data)
        return HttpResponseRedirect('?success=true')
    else:
        return render(request, 'landing/closet-cleanup.html')

@api_view(['GET', 'POST'])
def closet_cleanup2(request):
    if request.method == 'POST':
        data = request.data.copy()
        srlzr = LandingPageSrlzr2(data=data)
        if not srlzr.is_valid():
            return render(request, 'landing/closet-cleanup2.html', {'errors': srlzr.errors, 'data': data})
        data = {i:j for i,j in data.items()}
        ClosetCleanup.objects.create(**data)
        return HttpResponseRedirect('?success=true')
    else:
        return render(request, 'landing/closet-cleanup2.html')

@api_view(['GET', ])
@admin_only
def GetUsers(request):
    users = [{'id': i.id, 'name': i.zap_username + ' (' + i.email + ')', 'type': i.user_type.name} for i in
             ZapUser.objects.filter(zap_username__isnull=False, zap_username='ZapExclusive')] + [
                {'id': i.id, 'name': i.zap_username + ' (' + i.email + ')', 'type': i.user_type.name} for i in
                ZapUser.objects.filter(zap_username__isnull=False).exclude(zap_username='ZapExclusive').order_by('zap_username')]
    return Response({'status': 'success', 'data': users})


@api_view(['GET', 'POST'])
@admin_only
def GetAddress(request, u_id):
    if request.method == 'GET':
        addrss = Address.objects.filter(user_id=u_id)
        srlzr = GetAddressSerializer(addrss, many=True)
        return Response({'status': 'success', 'data': srlzr.data})
    elif request.method == 'POST':
        data = request.data.copy()
        data['user'] = u_id
        srlzr = AddressSerializer(data=data)
        if srlzr.is_valid():
            s = srlzr.save()
            srlzr = GetAddressSerializer(Address.objects.get(id=s.id))
            return Response({'status': 'success', 'data': srlzr.data})
        return Response({'status': 'error', 'detail': srlzr.errors})


@api_view(['GET', 'POST'])
@admin_only
def GetLogisticsEval(request):
    if request.method == 'GET':
        if 'partner' in request.GET:
            Q1 = Q(pickup_partner=request.GET['partner'])
            Q2 = Q(product_delivery_partner=request.GET['partner'])
            logistics_data = Logistics.objects.filter(Q1 | Q2).order_by('-id')
        else:
            logistics_data = Logistics.objects.all().order_by('-id')
        log_srlz = AdminLogisticsSerializer(logistics_data, many=True)
        data = {'log_data': log_srlz.data,
                'logistics_partners': [{'key': i[0], 'value': i[1]} for i in LOGISTICS_PARTNERS]}
        return Response({'status': 'success', 'data': data})  # srlzr.data})
    elif request.method == 'POST':
        data = request.data.copy()
        logistics = Logistics.objects.get(id=data['logistic'])
        # import pdb; ####pdb.set_trace()
        log_srlz = LogisticsSerializer(data=data)
        if log_srlz.is_valid():
            log_srlz.update(logistics, log_srlz.validated_data)
            ab = log_srlz.validated_data['consignor']
            consignor_add = ab.name + ", " + ab.address + ", " + ab.city + ", " + ab.state.name + ", " + ab.country + ", " + ab.pincode + ". Phone-" + ab.phone
            ce = log_srlz.validated_data['consignee']
            consignee_add = ce.name + ", " + ce.address + ", " + ce.city + ", " + ce.state.name + ", " + ce.country + ", " + ce.pincode + ". Phone-" + ce.phone
            pm_partner = dict(LOGISTICS_PARTNERS).get(log_srlz.validated_data['pickup_partner'])
            pro_partner = dict(LOGISTICS_PARTNERS).get(log_srlz.validated_data['product_delivery_partner'])
            return Response({'status': 'success',
                             'data': {'consignor': consignor_add, 'consignee': consignee_add, 'pm_partner': pm_partner,
                                      'pro_partner': pro_partner}})
        return Response({'status': 'error', 'detail': serlzr.errors})



        # return Response({'status': 'error', 'detail': srlzr.errors})


@api_view(['GET', 'POST'])
@admin_only
def GetProductsCount(request):
    if request.GET:
        cat = request.GET.get('cat')
        t = request.GET.get('type')
        data = []
        if cat == 'occasions':
            for q in Occasion.objects.all():
                if t == 'all':
                    loc_dict = {
                        'name' : q.name,
                        'approved':ApprovedProduct.ap_objects.filter(occasion=q).count(),
                        'tobeapproved':ApprovedProduct.pta_objects.filter(occasion=q).count(),
                        'disapproved':ApprovedProduct.dp_objects.filter(occasion=q).count()
                    }
                elif t == 'approved':
                    loc_dict = {
                        'name' : q.name,
                        'approved':ApprovedProduct.ap_objects.filter(occasion=q).count(),
                    }
                elif t == 'disapproved':
                    loc_dict = {
                        'name' : q.name,
                        'disapproved':ApprovedProduct.dp_objects.filter(occasion=q).count()
                    }
                elif t == 'tobeapproved':
                    loc_dict = {
                        'name' : q.name,
                        'tobeapproved':ApprovedProduct.pta_objects.filter(occasion=q).count(),

                    }
                data.append(loc_dict)
        elif cat == 'colors':
            for color in Color.objects.all():
                loc_dict = {
                    'name' : color.name,
                    'approved':ApprovedProduct.ap_objects.filter(color=color).count(),
                    'tobeapproved':ApprovedProduct.pta_objects.filter(color=color).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(color=color).count()

                }
                data.append(loc_dict)
        elif cat == 'categories':
            for subcat in SubCategory.objects.all():
                loc_dict = {
                    'name' : subcat.name,
                    'approved':ApprovedProduct.ap_objects.filter(product_category=subcat).count(),
                    'tobeapproved':ApprovedProduct.pta_objects.filter(product_category=subcat).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(product_category=subcat).count()

                }
                data.append(loc_dict)
        elif cat == 'styles':
            for style in Style.objects.all():
                loc_dict = {
                    'name' : style.style_type,
                    'approved':ApprovedProduct.ap_objects.filter(style=style).count(),
                    'tobeapproved':ApprovedProduct.pta_objects.filter(style=style).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(style=style).count()

                }
                data.append(loc_dict)
        elif cat == 'brands':
            if t == 'curated':
                data = [{'name':b.brand,'approved':b.c,'tobeapproved':0,'disapproved':0} for b in Brand.objects.filter(approvedproduct__status='1',approvedproduct__user__user_type__name='zap_exclusive').annotate(c=Count('approvedproduct')).filter(c__gt=0).order_by('-c')]
            elif t == 'market':
                data = [{'name':b.brand,'approved':b.c,'tobeapproved':0,'disapproved':0} for b in Brand.objects.filter(approvedproduct__status='1',approvedproduct__user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front']).annotate(c=Count('approvedproduct')).filter(c__gt=0).order_by('-c')]
            elif t == 'approved':
                data = [{'name':b.brand,'approved':b.c,'tobeapproved':0,'disapproved':0} for b in Brand.objects.filter(approvedproduct__status='1').annotate(c=Count('approvedproduct')).filter(c__gt=0).order_by('-c')]
            elif t == 'tobeapproved':
                data = [{'name':b.brand,'approved':0,'tobeapproved':b.c,'disapproved':0} for b in Brand.objects.filter(approvedproduct__status='0').annotate(c=Count('approvedproduct')).filter(c__gt=0).order_by('-c')]
            elif t == 'disapproved':
                data = [{'name':b.brand,'approved':0,'tobeapproved':0,'disapproved':b.c} for b in Brand.objects.filter(approvedproduct__status='2').annotate(c=Count('approvedproduct')).filter(c__gt=0).order_by('-c')]
            else:
                data = [{'name':b.brand,'approved':b.approvedproduct_set.filter(status='1').count(),'tobeapproved':b.approvedproduct_set.filter(status='0').count(),'disapproved':b.approvedproduct_set.filter(status='2').count()} for b in Brand.objects.annotate(c=Count('approvedproduct')).filter(c__gt=0).order_by('-c')]
                # for brand in Brand.objects.all():
                #     loc_dict = {
                #         'name': brand.brand,
                #         'approved': ApprovedProduct.objects.filter(brand=brand).count(),
                #         'tobeapproved': ProductsToApprove.objects.filter(brand=brand).count(),
                #         'disapproved': DisapprovedProduct.objects.filter(brand=brand).count()
                #     }
                #     data.append(loc_dict)
        elif cat == 'Age':
            for age in AGE:
                loc_dict = {
                    'name' : age[1],
                    'approved':ApprovedProduct.ap_objects.filter(age=age[0]).count(),
                    'tobeapproved':ApprovedProduct.pta_objects.filter(age=age[0]).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(age=age[0]).count()
                }
                data.append(loc_dict)
        elif cat == 'Condition':
            for cond in CONDITIONS:
                loc_dict = {
                    'name' : cond[1],
                    'approved':ApprovedProduct.ap_objects.filter(condition=cond[0]).count(),
                    'tobeapproved':ApprovedProduct.pta_objects.filter(condition=cond[0]).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(condition=cond[0]).count()
                }
                data.append(loc_dict)
        elif cat == 'sale':
            for sale in SALE_CHOICES:
                loc_dict = {
                    'name' : sale[1],
                    'approved':ApprovedProduct.ap_objects.filter(sale=sale[0]).count(),
                    'tobeapproved':ApprovedProduct.pta_objects.filter(sale=sale[0]).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(sale=sale[0]).count()
                }
                data.append(loc_dict)
        elif cat == 'Size':
            for s in Size.objects.all():
                loc_dict = {
                    'name' : s.size,
                    'approved':ApprovedProduct.ap_objects.filter(size__in=[s]).count(),

                    'tobeapproved':ApprovedProduct.pta_objects.filter(size__in=[s]).count(),
                    'disapproved':ApprovedProduct.dp_objects.filter(size__in=[s]).count()
                }
                data.append(loc_dict)
        elif cat == 'byview':
            data = {'max': ['data not available'], 'avg': 'data not available', 'with0': 'data not available'}
        elif cat == 'bylove':
            mx = ApprovedProduct.objects.all().annotate(max_count=Count('likes_got')).order_by('-max_count')
            data = {'max': [str(i.max_count) + ' (' + i.title + ')' for i in mx[0:3]],
                    'avg': mx.aggregate(sm=Sum('max_count'))['sm'] / float(mx.count()),
                    'with0': mx.filter(max_count=0).count()}
        elif cat == 'bycomment':
            mx = ApprovedProduct.objects.all().annotate(max_count=Count('comments_got')).order_by('-max_count')
            data = {'max': [str(i.max_count) + ' (' + i.title + ')' for i in mx[0:3]],
                    'avg': mx.aggregate(sm=Sum('max_count'))['sm'] / float(mx.count()),
                    'with0': mx.filter(max_count=0).count()}
        elif cat == 'byprice':
            sm_listing = ApprovedProduct.objects.aggregate(sm=Sum('listing_price'))['sm']
            sm_original= ApprovedProduct.objects.aggregate(sm=Sum('original_price'))['sm']
            total_prod = ApprovedProduct.ap_objects.filter(sale='2').count()
            data = {'listing':sm_listing/total_prod,'original':sm_original/total_prod,'discount':str((sm_original-sm_listing)/sm_original*100)+'%'}
        return Response({'status':'success','data':data})
    data = {'approved':ApprovedProduct.objects.count(),
            'disapproved':ApprovedProduct.dp_objects.count(),
            'tobeapproved':ApprovedProduct.pta_objects.count(),
            'incomplete':ApprovedProduct.ap_objects.filter(completed=False).count() + ApprovedProduct.dp_objects.filter(completed=False).count() + ApprovedProduct.pta_objects.filter(completed=False).count()
        }

    return Response({'status':'success','data':data})
@api_view(['GET','POST' ])
@admin_only
def GetUsersDetails(request):
    if request.GET:
        cat = request.GET.get('type')
        data = {}
        if cat == 'onboarding':
            data = [
                {'name': 'onboarding1', 'value': UserProfile.objects.filter(profile_completed='1').count()},
                {'name': 'onboarding2', 'value': UserProfile.objects.filter(profile_completed='2').count()},
                {'name': 'onboarding3', 'value': UserProfile.objects.filter(profile_completed='3').count()},
                {'name': 'onboarding4', 'value': UserProfile.objects.filter(profile_completed='4').count()},
                {'name': 'completed', 'value': UserProfile.objects.filter(profile_completed='5').count()}]
        elif cat == 'sex':
            data = [
                {'name': 'Male', 'value': UserProfile.objects.filter(sex='M').count()},
                {'name': 'Female', 'value': UserProfile.objects.filter(sex='F').count()}]
        elif cat == 'size':
            data = []
            for fs in Size.objects.all()[0:12]:
                data.append({'name': fs.size, 'value': UserPreference.objects.filter(foot_size=fs).count()})
        elif cat == 'brandtags':
            data = []
            for bt in BrandTag.objects.all():
                data.append({'name': bt.tag, 'value': UserPreference.objects.filter(brand_tags=bt).count()})
        elif cat == 'channel':
            data = [
                {'name': 'Facebook', 'value': UserProfile.objects.filter(user__logged_from__name='fb').count()},
                {'name': 'Instagram', 'value': UserProfile.objects.filter(user__logged_from__name='instagram').count()},
                {'name': 'Email', 'value': UserProfile.objects.filter(user__logged_from__name='zapyle').count()}]
        elif cat == 'device':
            data = [
                {'name': 'Android', 'value': ZapUser.objects.filter(logged_device__name='android').count()},
                {'name': 'IOS', 'value': ZapUser.objects.filter(logged_device__name='ios').count()},
                {'name': 'Website', 'value': ZapUser.objects.filter(logged_device__name='website').count()}]
        elif cat == 'upload':
            mx = ZapUser.objects.annotate(max_count=Count('approved_product')).order_by('-max_count')
            sm = ZapUser.objects.all().annotate(max_count=Count('approved_product')).aggregate(Sum('max_count'))[
                'max_count__sum']
            tot = ZapUser.objects.count()
            data = {'max': [str(i.max_count or '') + ' (' + (i.zap_username or '') + ')' for i in mx[0:10]],
                    'avg': sm / float(tot), 'with0': ZapUser.objects.filter(approved_product__isnull=True).count()}
        elif cat == 'admirer':
            mx = UserProfile.objects.annotate(max_count=Count('admiring')).order_by('-max_count')
            data = {'max': [str(i.max_count) + ' (' + i.user.zap_username + ')' for i in mx[0:10]],
                    'avg': UserProfile.objects.aggregate(a=Count('admiring'))['a'] / float(mx.count()),
                    'with0': UserProfile.objects.filter(admiring__isnull=True).count()}
        elif cat == 'admiring':
            mx = ZapUser.objects.all().annotate(max_count=Count('aaaa')).order_by('-max_count')
            data = {'max': [str(i.max_count) + ' (' + i.zap_username + ')' for i in mx[0:10]],
                    'avg': mx.aggregate(sm=Sum('max_count'))['sm'] / float(mx.count()),
                    'with0': mx.filter(max_count=0).count()}
        elif cat == 'love':
            mx = ZapUser.objects.all().annotate(max_count=Count('loved_products')).order_by('-max_count')
            data = {'max': [str(i.max_count) + ' (' + i.zap_username + ')' for i in mx[0:10]],
                    'avg': mx.aggregate(sm=Sum('max_count'))['sm'] / float(mx.count()),
                    'with0': mx.filter(max_count=0).count()}
        elif cat == 'comment':
            mx = ZapUser.objects.all().annotate(max_count=Count('commenter')).order_by('-max_count')
            data = {'max': [str(i.max_count) + ' (' + i.zap_username + ')' for i in mx[0:10]],
                    'avg': mx.aggregate(sm=Sum('max_count'))['sm'] / float(mx.count()),
                    'with0': mx.filter(max_count=0).count()}
        return Response({'status': 'success', 'data': data})
    total = ZapUser.objects.count()
    yesterday = date.today() - timedelta(1)
    data = {
        'total': total,
        'sessions': ZapSession.objects.count(),
        'yesterday': ZapUser.objects.filter(last_login__gte=yesterday).count(),
        'joined': ZapUser.objects.filter(date_joined__gte=yesterday).count(),
        'new_users': [{'username': (z.zap_username or ''), 'email': (z.email or ''),
                       'logged_from': (z.logged_from.name or 'undefined'),
                       'device': (z.logged_device.name or 'undefined'),
                       'time': timesince.timesince(z.date_joined) + " ago."}
                      for z in ZapUser.objects.filter(date_joined__gte=yesterday)],
        'verified_email': ZapUser.objects.filter(email_verified=True).count(),
        'verified_phone': ZapUser.objects.filter(phone_number_verified=True).count(),
        'description': UserProfile.objects.filter(description__isnull=False).count(),
        'profile_pic': UserProfile.objects.filter(user__logged_from__name='zapyle', _profile_pic__isnull=False).count(),
        'email_users': UserProfile.objects.filter(user__logged_from__name='zapyle').count()
    }
    return Response({'status': 'success', 'data': data})


@api_view(['GET', 'POST'])
@admin_only
def GetOrdersDetails(request):
    if request.GET:
        cat = request.GET.get('type')
        if cat == 'origin':
            data = Address.objects.all().annotate(c=Count('trans_buyer')).filter(c__gt=0).values('city').annotate(cnt=Count('city')).order_by('-cnt')
            # data = Address.objects.all().annotate(cnt=Count('trans_buyer')).filter(cnt__gt=0).values('city', 'cnt').order_by('cnt')
        elif cat == 'destination':
            data = Address.objects.all().annotate(c=Count('order_seller')).filter(c__gt=0).values('city').annotate(cnt=Count('city')).order_by('-cnt')
            # data = Address.objects.all().annotate(cnt=Count('order_seller')).filter(cnt__gt=0).values('city', 'cnt').order_by('cnt')
        return Response({'status': 'success', 'data': data})
    total = Order.objects.count()
    # withCoupon = Order.objects.filter(transaction__cart__coupon__isnull=False)
    withCouponCnt = 0#withCoupon.count()
    s = datetime.timedelta(0, 0)
    ordr = Order.objects.filter(delivery_date__isnull=False).values_list('delivery_date', 'placed_at')
    for o in ordr:
        s += o[0] - o[1]
    yesterday = date.today() - timedelta(1)
    data = {
        'total': total,
        'avg_price': Order.objects.aggregate(Sum('transaction__final_price'))['transaction__final_price__sum'] / total if
        Order.objects.aggregate(Sum('transaction__final_price'))['transaction__final_price__sum'] else 0,
        'withCoupon': (str(withCouponCnt) + ' (' + str(
            withCouponCnt / float(total) * 100) + '%)') if total else withCouponCnt if withCouponCnt else 0,
        'avg_delivery': str(s.days) + 'days',
        'avg_disc': 'data not available',
        'transCount': Transaction.objects.filter(time__gte=yesterday).count(),
        'transDetails': [
            'ID' + str(t.id) + ' ' + ('SUCCESS' if t.success else 'FAILED') + ' ' + t.buyer.email + ' -- ' + (
            t.cart.items.all()[
                0].product.title if t.cart.items.all() else 'Item Not Found') + ' -- ' + timesince.timesince(
                t.time) + " ago." for t in Transaction.objects.filter(time__gte=yesterday)],
    }
    return Response({'status': 'success', 'data': data})


@api_view(['GET', 'POST'])
@admin_only
def GetActionDatas(request):
    action = request.GET.get('action')
    if action == 'product':
        data = [{'id': p.id, 'name': p.title} for p in ApprovedProduct.objects.all()]
    elif action == 'profile':
        data = [{'id': u.id, 'name': (u.zap_username or '') + ' ' + '({})'.format(u.email)} for u in
                ZapUser.objects.all()]
    return Response({'status': 'success', 'data': data})


@api_view(['GET', 'POST'])
@admin_only
def get_upload_details(request):
    states = State.objects.all()
    states_srlzr = StateSerializer(states, many=True)
    categories = Category.objects.all()
    categories_srlzr = GetCategorySerializer(categories, many=True)
    subc = SubCategory.objects.all()
    subcat_srlzr = SubCategorySerializer(subc, many=True)
    global_size = Size.objects.all().exclude(category_type="FS")
    global_size_srlzr = SizeSerializer(global_size, many=True)
    brand_list = Brand.objects.all().order_by('brand')
    brand_srlzr = BrandSerializer(brand_list, many=True)
    occasion = Occasion.objects.all()
    occasion_srlzr = OccasionSerializer(occasion, many=True)
    color = Color.objects.all()
    color_srlzr = ColorSerializer(color, many=True)
    styles = Style.objects.all()
    style_srlzr = StyleSerializer(styles, many=True)
    u = ZapUser.objects.get(zap_username="ZapExclusive")
    zapexc = {'id':'{},zap_exclusive'.format(u.id), 'email':'{} ({})'.format(u.zap_username,u.email)}
    return Response({'status': 'success', 'data': {'brands': brand_srlzr.data,
                                                   'fashion_types': style_srlzr.data,
                                                   'category': categories_srlzr.data,
                                                   'global_product_list': global_size_srlzr.data,
                                                   'sub_category': subcat_srlzr.data,
                                                   'occasion': occasion_srlzr.data,
                                                   'color': color_srlzr.data,
                                                   'states': states_srlzr.data,
                                                   'zap_exc_user':zapexc}})


@api_view(['GET', 'POST'])
@admin_only
def LogisticsRejection(request):
    log = LogisticsLog.objects.filter(track=True, pickup=True, status="Delivered")
    serlzr = LogisticsLogRejectSerializer(log, many=True)
    return Response({'status': 'success', 'data': serlzr.data})


@api_view(['GET', 'POST'])
@admin_only
def done_process(request):
    if request.method == 'GET':
        logistic = []
        for l in Logistics.objects.order_by('-id'):
            logis = l.logistics_log.all()
            logs = [{
                        'log': l.id, 'id': i.id, 'rowspan': logis.count(),
                        'consignee': l.consignee.name, 'consignor': l.consignor.name,
                        'initiate_payout': all(l.orders.all().values_list('transaction__initiate_payout', flat=True)),
                        'paid_out': all(l.orders.all().values_list('transaction__paid_out', flat=True)),
                        'time': i.triggered_pickup_at, 'status': i.status, 'pickup': i.pickup} for i in logis]
            logistic = logistic + logs
        return Response({'status': 'success', 'data': logistic})
    else:
        trans_ids = Logistics.objects.filter(id=request.data['log_id']).values_list('orders__transaction__id',
                                                                                    flat=True)
        if trans_ids:
            payouts(trans_ids)
        return Response({'status': 'success'})


@api_view(['GET', 'POST'])
@admin_only
def in_process(request):
    if request.method == 'GET':
        logistics = [{
                         'orders': [{
                                        'id': o.id, 'order_number': o.order_number} for o in l.orders.all()],
                         'returns': [{
                                         'id': r.id, 'order_number': r.order_id.order_number} for r in l.returns.all()],
                         'id': l.id,
                         'triggered_pickup': l.triggered_pickup,
                         'pickup_partner': l.pickup_partner,
                         'product_delivery_partner': l.product_delivery_partner,
                         'confirmed_at': l.confirmed_at,
                         'consignee': l.consignee.name,
                         'consignor': l.consignor.name,
                         'zap_inhouse': l.zap_inhouse,
                         'pick_status': l.logistics_log.get(pickup=True).status if l.logistics_log.filter(
                             pickup=True) else '',
                         'del_status': l.logistics_log.get(pickup=False).status if l.logistics_log.filter(
                             pickup=False) else '',
                         'verified': l.logistics_log.filter(pickup=True, product_verified=True).count(),
                         'trigger_delivery': l.logistics_log.filter(pickup=False).count(),
                         'pick_delivered': l.logistics_log.filter(pickup=True, status="Delivered").count()} for l in
                     Logistics.objects.order_by('-id').distinct()]
        return Response({'status': 'success', 'data': logistics})
    else:
        data = request.data.copy()
        logistic = Logistics.objects.get(id=data['logistic'])
        if data['action'] == 'trigger':
            if data.get('order', ''):
                pickup_orders_logistics(data['logistic'])
            elif data.get('return', ''):
                pickup_returns_logistics(data['logistic'])
                # logistic.triggered_pickup = True
                # logistic.save()
        elif data['action'] == 'trigger_delivery':
            pickup_update(data['logistic'], 'normal')
        elif data['action'] == 'verify_logistics':
            LogisticsLog.objects.filter(logistics=logistic, pickup=True).update(product_verified=True)
        else:
            order = Order.objects.get(id=data['order'])
            logistic.orders.remove(order)
            order.rejected = True
            order.save()
        return Response({'status': 'success'})


@api_view(['GET', 'POST'])
@admin_only
def before_process(request):
    if request.method == 'GET':
        orders = [{
                      'type': 'order', 'id': o.id, 'order_number': o.order_number,
                      'time': o.placed_at, 'triggered_logistics': o.triggered_logistics,
                      'consignee': o.consignee.name + ' ' + o.consignee.address,
                      'consignor': o.consignor.name + ' ' + o.consignor.address,
                      'cancelled': o.cancelled} for o in
                  Order.objects.filter(triggered_logistics=False, confirmed_with_buyer=True,
                                       confirmed_with_seller=True)]
        returns = [{
                       'type': 'return', 'time': r.requested_at, 'id': r.id,
                       'cancelled': r.rejected,
                       'consignee': r.consignee.name + ' ' + r.consignee.address,
                       'consignor': r.consignor.name + ' ' + r.consignor.address} for r in
                   Return.objects.filter(triggered_logistics=False, approved=True, self_return=False)]
        merge_list = orders + returns
        newlist = sorted(merge_list, key=itemgetter('time'), reverse=True)

        return Response({'status': 'success', 'data': newlist})
    else:
        data = request.data.copy()
        print data,'dataaaaaaaa'
        if data['status'] == 'logistics':
            partners = {}
            if data['type'] == 'order':
                # o = Order.objects.get(id=data['id'])
                # o_ids = Order.objects.filter(transaction__consignee=o.transaction.consignee, consignor=o.consignor, order_status='confirmed',
                #                             ).values_list('id', flat=True)
                o_ids = Order.objects.filter(id=data['id'], order_status='confirmed').values_list('id', flat=True)
                partners = logistics_evaluator(o_ids, None)
            else:
                r = Return.objects.get(id=data['id'])
                o_ids = Return.objects.filter(consignee=r.consignee, consignor=r.consignor, triggered_logistics=False,
                                              approved=True, self_return=False, rejected=False).values_list('id',
                                                                                                            flat=True)
                status = logistics_evaluator(None, o_ids)

            return Response({'status': 'success', 'data': o_ids,'partners':partners})
        elif data['status'] == 'pickup':
            # Logistics.objects.get(orders=data['id'])
            pickup_orders_logistics(Logistics.objects.get(orders=data['id']).id)
        elif data['status'] == 'delivery':
            if data['delivery_type'] == 'normalDelivery':
                logistic = Logistics.objects.filter(orders=data['id'])[0].id
                pickup_update(logistic, 'normal')
            else:
                logistic = Logistics.objects.filter(orders=data['id']).last().id
                pickup_update(logistic, 'rejected_delivery')
        elif data['status'] == 'amzadDelivery':
            try:
                log = LogisticsLog.objects.get(logistics__orders=data['id'],pickup=False,returns=False)
            except LogisticsLog.DoesNotExist:
                logistic = Logistics.objects.get(orders=data['id'])
                delivery_data = {'logistics': logistic.id, 'track': True, 'pickup':False,'log_status':0, 'logistics_ref': str(logistic.id), 'partner': 'ZP'}
                from zap_apps.logistics.logistics_serializer import LogisticsLogSerializer
                log = LogisticsLogSerializer(data=delivery_data)
                if log.is_valid():
                    log.save()
                    log = LogisticsLog.objects.get(id=log.data['id'])
                    logistic.triggered_pickup = True
                    logistic.save()
                else:
                    print logistic.errors,' error 1242'
                    return Response({'status':'error'})
            if log.log_status == 0:
                log.log_status = 2
                log.save()
                update_order_status(2,log)
            elif not log.log_status == 4:
                log.log_status = 4
                log.save()
                update_order_status(4,log)
            else:
                return Response({'status':'error'})
        elif data['status'] == 'amzadPicked':
            try:
                log = LogisticsLog.objects.get(logistics__orders=data['id'],pickup=True,returns=False)
            except LogisticsLog.DoesNotExist:
                logistic = Logistics.objects.get(orders=data['id'])
                pickup_data = {'logistics': logistic.id, 'track': True, 'logistics_ref': str(logistic.id), 'partner': 'ZP'}
                from zap_apps.logistics.logistics_serializer import LogisticsLogSerializer
                log = LogisticsLogSerializer(data=pickup_data)
                if log.is_valid():
                    log.save()
                    log = LogisticsLog.objects.get(id=log.data['id'])
                    logistic.triggered_pickup = True
                    logistic.save()
                else:
                    print logistic.errors,' error 1250'
                    return Response({'status':'error'})
            if not log.log_status == 4:
                if data['activity'] == 'picked':
                    status = 2
                else:
                    status = 4
                log.log_status = status
                log.save()
                update_order_status(status,log)
            else:
                return Response({'status':'error'})
        elif data['status'] == 'change_partner':
            logistic = Logistics.objects.filter(orders=data['id'])[0]
            if data['type'] == 'pickup':
                logistic.pickup_partner = data['partner']
            else:
                logistic.product_delivery_partner = data['partner']
            logistic.save()
        elif data['status'] == 'cancel':
            order = Order.objects.get(id=data['id'])
            size_text = order.ordered_product.size
            size = size_text.split('_')
            if size[0] == 'FREESIZE':
                s = Size.objects.get(category_type="FS")
            elif size[0] == 'US':
                s = Size.objects.get(us_size=size[1])
            elif size[0] == 'UK':
                s = Size.objects.get(uk_size=size[1])
            elif size[0] == 'EU':
                s = Size.objects.get(eu_size=size[1])
            order.product.product_count.filter(size=s).update(quantity=F('quantity') + order.quantity)
            order.order_status = 'cancelled'
            order.save()
            OrderTracker.objects.create(orders_id=data['id'],status='cancelled')

        else:
            if data['type'] == 'order':
                obj = Order.objects.get(id=data['id'])
                obj.cancelled = True if data['status'] == 'cancel' else False
            else:
                obj = Return.objects.get(id=data['id'])
                obj.rejected = True if data['status'] == 'cancel' else False
            obj.save()
        return Response({'status': 'success', 'data': 'updated'})


@api_view(['GET',])
@admin_only
def seller_buyer_account(request):
    order = Order.objects.get(order_number=request.GET['order_number'])
    seller = order.consignor.user
    sellerDict = {'ifsc':'','number':'','email':'','phone':''}
    if seller.user_type.name == 'zap_exclusive':
        ac = order.product.zapexclusiveuserdata_set.first()
        if ac:
            sellerDict = {'ifsc':ac.ifsc_code,'number':decryptAcc(ac.account_number) if ac.account_number else '','email':ac.email,'phone':ac.phone_number}
    else:
        ac = seller.user_data
        if ac:
            sellerDict = {'ifsc':ac.ifsc_code,'number':decryptAcc(ac.account_number) if ac.account_number else '','email':seller.email,'phone':order.consignor.phone}
    buyer = order.transaction.consignee.user
    ac = buyer.user_data
    buyer = {'ifsc':ac.ifsc_code,'number':decryptAcc(ac.account_number) if ac.account_number else '','email':buyer.email,'phone':order.transaction.consignee.phone}
    data = {'seller':sellerDict,'buyer':buyer}
    return Response({'status':'success','data':data})

@api_view(['POST',])
@admin_only
def verify_pickedup(request):
    if request.method == 'POST':

        data = request.data.copy()
        print data,'---------------'
        status = data['status']
        Order.objects.filter(id=data['id'],order_status='verification').update(order_status=status, product_verification=status.replace('product_',''))
        OrderTracker.objects.create(orders_id=data['id'],status=data['status'])
        print data['status']
        return Response({'status':'success'})

@api_view(['POST',])
@admin_only
def trigger_return(request):

    if request.method == 'POST':
        data = request.data.copy()
        partners = rejected_products(data['order_id'])
        return Response({'status':'success', 'partners':partners})

@api_view(['POST',])
@admin_only
def return_trigger(request):

    if request.method == 'POST':
        # pdb.set_trace()
        data = request.data.copy()
        partners = {}
        print data,'ssssssssssssssss'
        if data['step'] == 'pickup':
            pickup_returns_logistics(Logistics.objects.get(returns=data['return_id'], triggered_pickup=False).id)
        elif data['step'] == 'delivery':
            print 'developing code ...'
        elif data['step'] == 'approve':
            r = Return.objects.get(id=data['return_id'])
            r.product_verification = 'approved'
            r.return_status = 'product_approved'
            r.save()
        else:
            r = Return.objects.get(id=data['return_id'])
            r_ids = Return.objects.filter(id=data['return_id'], return_status='confirmed').values_list('id', flat=True)
            partners = logistics_evaluator(None, r_ids)
        
        return Response({'status':'success', 'partners':partners})

@api_view(['GET',])
@admin_only
def LoadUsers(request):
    serlzr = ChangeUserProductSerlzr(ZapUser.objects.all(), many=True)
    return Response({'status': 'success', 'data': serlzr.data})


@api_view(['GET', ])
@admin_only
def LoadUserAddressess(request):
    data = [{'id': a.id, 'name': a.name, 'address': a.address, 'phone': a.phone} for a in Address.objects.filter()]
    return Response({'status': 'success', 'data': data})


@api_view(['GET', 'POST'])
@admin_only
def UpdateProduct(request):
    product = ApprovedProduct.pta_objects.get(id=request.GET['product_id'])
    parcel_data = parcelled_pickup_check([product.pickup_address.pincode] if product.pickup_address else [])
    serlzr = ProductsToApproveSerializer2(product, context={'parcel_data': parcel_data['data']})
    return Response({'status': 'success', 'data': serlzr.data})


@api_view(['GET', 'POST'])
@admin_only
def EditProduct(request):
    if request.method == 'GET':
        p_id = request.GET.get('p_id','')
        product = ApprovedProduct.objects.get(id=p_id)
        serlzr = UpdateApprovedProductsSerializer(product)
        return Response({'status':'success', 'data':serlzr.data})
    else:
        data = request.data.copy()
        # data['update_time'] = timezone.now()
        product = ApprovedProduct.objects.get(id=data['id'])
        if data['sale'] == '1':   
            serlzr = SocialProductSerializer(data=data)
        else:
            serlzr = SaleProductSerializer(data=data)
        if serlzr.is_valid():
            sorted_ids = [i['id'] for i in sorted(data['images'], key=itemgetter('pos'))]
            img_ids = list(sorted_ids)
            sorted_ids.sort()
            if sorted_ids == img_ids:
                data['images'] = sorted_ids
            else:
                data['images'] = []
                for id in img_ids:
                    img = ProductImage.objects.get(id=id)
                    img.pk = None
                    while True:
                        try:
                            img.save()
                            break
                        except IntegrityError:
                            pass
                    data['images'].append(img.id)
                ProductImage.objects.filter(id__in=img_ids).delete()
            data['completed'] = True
            if data['sale'] == '2':   
                data['discount'] = (float(data['original_price']) - float(data['listing_price'])) / float(data['original_price'])
            user = ZapUser.objects.get(id=data['user'])
            data['with_zapyle'] = True if user.user_type.name in ['zap_exclusive', 'zap_dummy'] or data['with_zapyle'] else False
            serlzr = UpdateApprovedProductsSerializer(product, data=data, partial=True)
            old_images = product.images.all().exclude(id__in=data['images'])
            if serlzr.is_valid():
                old_images.delete()
                serlzr.save()
                try:
                    if product.zapexclusiveuserdata_set.all():
                        try:
                            product.zapexclusiveuserdata_set.all()[0].products_to_approve.remove(product)
                        except (ValueError, IndexError):
                            product.zapexclusiveuserdata_set.all()[0].products.remove(product)
                except AttributeError:
                    print 'zapexclusive data not found for disapproved products.. need discussion'
                user = ZapUser.objects.get(id=data['user'])
                if (user.user_type.name == 'zap_exclusive' or user.user_type.name == 'zap_dummy') and data[
                    'sale'] == '2':
                    zapexc = ZapExclusiveUserData.objects.get(email=data['email'])
                    zapexc.products.add(product)
                if not user.user_type.name == 'store_front':
                    data['size_selected'] = [data['size_selected'][0]]

                NumberOfProducts.objects.filter(product=product).delete()
                for i in data['size_selected']:
                    if data['size_selected'][0]['size_type'] == 'FREESIZE':
                        i['size'] = Size.objects.get(category_type="FS")
                        NumberOfProducts.objects.create(product=product, quantity=i['quantity'],size=i['size'])
                    else:
                        NumberOfProducts.objects.create(product=product, quantity=i['quantity'],size_id=i['size'])
                return Response({'status':'success','data':'Succesfully Updated'})
            else:
                return Response({'status': 'error', 'detail': serlzr.errors})
        else:
            print serlzr.errors
            return Response({'status': 'error', 'detail': serlzr.errors})


@api_view(['GET', 'POST'])
@admin_only
def UserAccountNumberByAdmin(request, pk):
    if request.method == 'GET':
        obj, c = UserData.objects.get_or_create(user_id=pk)
        account_number = obj.account_number or ""
        if account_number:
            account_number = decrypt(account_number)
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
    else:
        data = request.data.copy()
        data['user_id'] = pk
        srlzr = UserDataSerializer(data=data)
        if not srlzr.is_valid():
            return Response({'status': 'error', 'detail': srlzr.errors})
        obj, c = UserData.objects.get_or_create(user=pk)
        obj.old_account_number = obj.account_number
        obj.account_number = encrypt(data['account_number'])
        obj.ifsc_code = request.data['ifsc_code']
        obj.account_holder = request.data.get('account_holder')
        obj.save()
        if not c:
            user = ZapUser.objects.get(id=pk)
            if user.phone_number:
                zapsms = ZapSms()
                zapsms.send_sms(user.phone_number, settings.ACCOUNT_NUM_CHANGED_MSG)
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
        return Response({'status': 'success', 'data': 'Account number updated succesfully.'})


def decrypt(account_number):
    obj = DES.new(ENCKEY, DES.MODE_ECB)
    cipher_user_acc_no = base64.b64decode(account_number)
    user_acc_no_dummy = obj.decrypt(cipher_user_acc_no)
    user_acc_no = re.sub('[Z]', '', user_acc_no_dummy)
    return user_acc_no


def encrypt(account_number):
    obj = DES.new(ENCKEY, DES.MODE_ECB)
    plain = account_number
    modified = plain + (16 - len(plain)) * 'Z'
    ciph = obj.encrypt(modified)
    second_encp = base64.b64encode(ciph)
    return second_encp


@api_view(['GET', 'POST', 'PUT'])
@admin_only
def load_zapexc_accounts(request):
    if request.method == 'GET':
        data = [{'account_number': decrypt(i.account_number) if i.account_number else None,
                 'account_holder': i.account_holder, 'phone_number': i.phone_number, 'email': i.email,
                 'ifsc_code': i.ifsc_code, 'full_name': i.full_name} for i in ZapExclusiveUserData.objects.all()]
        return Response({'status': 'success', 'data': data})
    elif request.method == 'POST':
        data = request.data
        if 'account_number' in data and data['account_number']:
            obj = DES.new(ENCKEY, DES.MODE_ECB)
            plain = data['account_number']
            modified = plain + (16 - len(plain)) * 'Z'
            ciph = obj.encrypt(modified)
            second_encp = base64.b64encode(ciph)
            data['account_number'] = second_encp
        zap_exc, c = ZapExclusiveUserData.objects.get_or_create(email=data['email'])
        zapexc = ZapExclusiveUserDataSerializer(zap_exc, data=data, partial=True)
        if zapexc.is_valid():
            zapexc.save()
        return Response({'status': 'success'})
    elif request.method == 'PUT':
        data = request.data.copy()
        zapexc = ZapExclusiveUserData.objects.filter(products=data['id'])
        if zapexc:
            return Response({'status': 'success', 'email': zapexc[0].email})
        return Response({'status': 'error'})


@api_view(['GET', 'POST', ])
@admin_only
def Dashboard(request):
    if request.method == 'GET':
        return render(request, 'dashboard/dashboard.html')
    elif request.method == 'POST':
        today = date.today()
        if request.GET.get('action') == 'graph':
            dates, joined, logged = [], [], []
            startDate1 = date.today() - timedelta(10)
            for n in range(9, -1, -1):
                dayStart = (today - timedelta(days=n))
                dayEnd = (today - timedelta(days=n - 1))
                joined.append(ZapUser.objects.filter(date_joined__gte=dayStart, date_joined__lte=dayEnd).count())
                logged.append(ZapUser.objects.filter(last_login__gte=dayStart, last_login__lte=dayEnd).count())
                dates.append(dayStart)
            t = {
                'users':ZapUser.objects.count(),
                't_users':ZapUser.objects.filter(date_joined__gte=today).count(),
                'products':ApprovedProduct.ap_objects.count(),
                't_products':ApprovedProduct.ap_objects.filter(upload_time__gte=today).count(),
                'orders':Order.objects.count(),
                't_orders':Order.objects.filter(placed_at__gte=today).count(),
                'returns':Return.objects.count(),
                't_returns':Return.objects.filter(requested_at__gte=today).count()
            }
            return Response({'status': 'success', 'dates': dates, 'joined': joined, 'logged': logged, 'total': t})
        elif request.GET.get('action') == 'listing_graph':
            dates, listing_tobeapproved, listing_approved, listing_disapproved = [], [], [], []
            startDate1 = date.today() - timedelta(10)
            for n in range(9, -1, -1):
                dayStart = (today - timedelta(days=n))
                dayEnd = (today-timedelta(days=n-1))
                listing_tobeapproved.append(ApprovedProduct.pta_objects.filter(upload_time__gte=dayStart,upload_time__lte=dayEnd).count())
                listing_approved.append(ApprovedProduct.ap_objects.filter(upload_time__gte=dayStart,upload_time__lte=dayEnd).count())
                listing_disapproved.append(ApprovedProduct.dp_objects.filter(upload_time__gte=dayStart,upload_time__lte=dayEnd).count())
                dates.append(dayStart)
            return Response({'status': 'success', 'dates': dates, 'listing': [x + y + z for x, y, z in
                                                                              zip(listing_tobeapproved,
                                                                                  listing_approved,
                                                                                  listing_disapproved)]})
        elif request.GET.get('action') == 'order_graph':
            dates, order_list = [], []
            startDate1 = date.today() - timedelta(10)
            for n in range(9, -1, -1):
                dayStart = (today - timedelta(days=n))
                dayEnd = (today - timedelta(days=n - 1))
                order_list.append(Order.objects.filter(placed_at__gte=dayStart, placed_at__lte=dayEnd).count())
                dates.append(dayStart)
            return Response({'status': 'success', 'dates': dates, 'order': order_list})
        if request.GET.get('action') == 'device':
            t = ZapUser.objects.aggregate(
                ios_today=Count(
                    Case(When(logged_device__name='ios', date_joined__gte=today, then=1), output_field=IntegerField())),
                ios_total=Count(Case(When(logged_device__name='ios', then=1), output_field=IntegerField())),
                android_today=Count(Case(When(logged_device__name='android', date_joined__gte=today, then=1),
                                         output_field=IntegerField())),
                android_total=Count(Case(When(logged_device__name='android', then=1), output_field=IntegerField())),
                website_today=Count(Case(When(logged_device__name='website', date_joined__gte=today, then=1),
                                         output_field=IntegerField())),
                website_total=Count(Case(When(logged_device__name='website', then=1), output_field=IntegerField())),
                fb_total=Count(Case(When(logged_from__name='fb', then=1), output_field=IntegerField())),
                fb_today=Count(
                    Case(When(logged_from__name='fb', date_joined__gte=today, then=1), output_field=IntegerField())),
            )
            return Response({'status': 'success', 'total': t})
        else:
            t = {}
            if request.GET.get('date') != 'undefined':
                ZapUsers = ZapUser.objects.filter(date_joined__startswith=request.GET.get('date'))
            else:
                ZapUsers = ZapUser.objects.filter(date_joined__gte=today)
            users = [{'onboarding': z.profile.profile_completed, 'image': z.profile.profile_pic,
                      'username': (z.zap_username or ''), 'email': (z.email or ''),
                      'logged_from': (z.logged_from.name or 'undefined'),
                      'device': (z.logged_device.name or 'undefined'),
                      'time': timesince.timesince(z.date_joined) + " ago."}
                     for z in ZapUsers]
            return Response({'status': 'success', 'users': users})




def export_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email'])
    for i in ZapUser.objects.all():
        try:
            writer.writerow([i.get_full_name() or i.zap_username or "", i.email])
        except:
            pass
    return response

def export_seller_details(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'First upload date', 'Last Update', 'join Date', 'Number of products uploaded', 'Number of products approved'])
    for i in ZapUser.objects.annotate(t=Count('approved_product')).filter(t__gt=0).order_by('-t'):
        try:
            writer.writerow([i.get_full_name() or i.zap_username or "",
                             i.approved_product.order_by('upload_time')[0].upload_time,
                             i.approved_product.order_by('upload_time')[0].update_time, 
                             i.date_joined, 
                             i.approved_product.count(), 
                             i.approved_product.filter(status=1).count()])
        except:
            pass
    return response


def export_website_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Joined'])
    p = datetime.date(2016, 3, 16)
    for i in ZapUser.objects.filter(logged_device__name='website').exclude(date_joined__startswith=p):
        try:
            writer.writerow(
                [i.get_full_name() or i.zap_username or "", i.email or "", i.phone_number or "", i.date_joined])
        except:
            pass
    return response


def export_order_view(request, confirmed):
    url = get_current_site(request)
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['Order Number', 'Product', 'Product Id', 'Listing Price', 'Total Price', 'Final Price', 'Seller', 'Seller_Phone', 'Buyer', 'Buyer_phone', 'Payment Mode',
         'status', 'Date_of_order', 'Date_of_upload', 'url'])
    p = datetime.date(2016, 3, 16)
    orders = Order.objects.order_by('-id')
    if confirmed == 'confirmed':
        orders = orders.exclude(order_status='cancelled').exclude(order_status='return_in_process').order_by('-id')
    for o in orders:
    
        try:
            writer.writerow([o.order_number, o.ordered_product.title, o.product.id, o.final_price,
                             o.transaction.total_price_with_shipping_charge(),
                             o.transaction.final_price,
                             o.consignor.user.get_full_name()+' '+o.consignor.city,
                             o.consignor.user.phone_number or "",
                             o.transaction.consignee.user.get_full_name()+' '+o.transaction.consignee.city,
                             o.transaction.consignee.user.phone_number or "",
                             o.transaction.get_payment_mode_display(),
                             o.order_status,
                             o.placed_at,
                             o.product.upload_time,
                             '{}/#/product/{}'.format(url, o.product.id)])
        except:
            pass
    return response
@api_view(['GET', 'POST', ])
def export_user(request):
    params = request.GET
    label = []
    if params:
        if params.get('email'):
            label.append('Email')
            e = True
        if params.get('phone'):
            label.append('Phone')
            p = True
        if params.get('wallet'):
            label.append('Wallet')
            w = True
        if params.get('sort') == 'wallet':
            users = ZapUser.objects.annotate(m=Sum('zapcash_user1__amount')).order_by('m')
        else:
            users = ZapUser.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
        writer = csv.writer(response)
        # writer.writerow(['Name', 'Email', 'Phone'])
        writer.writerow(label)
        for i in users:
            try:
                d = []
                if e:
                    d.append(i.email or "")
                if p:
                    d.append(i.phone_number or "")
                if w:
                    d.append(i.get_zap_wallet)
                writer.writerow(d)
            except:
                pass
        return response
    else:
        return Response({'status':'error','detail':'include parameters. eg: www.zapyle.com/zapadmin/export/user/?wallet=1&phone=1&email=1'})

def export_user_credit_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Gender', 'Joined', 'Credits', 'Credits Used', 'Cash Used'])
    # p = datetime.date(2016, 3, 16)
    for i in ZapUser.objects.all():
        try:
            transactions = i.buyer.all()
            zap_credits = sum([t.zapcredit_used for t in transactions])
            zap_cash = sum([t.zapcash_used for t in transactions])
            writer.writerow(
                [i.get_full_name() or i.zap_username or "", i.email or "", i.phone_number or "", i.profile.sex,
                 i.date_joined, i.get_zap_credit(), zap_credits, zap_cash])
        except:
            pass
    return response


def export_user_preference_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['ZapUsername', 'Name', 'Email', 'Phone', 'Gender', 'FirstName', 'Joined', 'waist_size', 'foot_size(US)', 'cloth_size', 'brand'])
    p = datetime.date(2016, 3, 16)
    for i in ZapUser.objects.filter():  # zap_username__isnull=False):
        try:
            if hasattr(i, 'fashion_detail'):
                writer.writerow([i.zap_username or "", i.get_full_name() or i.zap_username or "", i.email or "", \
                                 i.phone_number or "", i.profile.sex, i.first_name,i.date_joined, \
                                 ', '.join(i.fashion_detail.waist_size.all().values_list('size', flat=True)), \
                                 ', '.join(str(x) for x in
                                           i.fashion_detail.foot_size.all().values_list('foot_size', flat=True)), \
                                 ', '.join(i.fashion_detail.size.all().values_list('size', flat=True)), \
                                 ', '.join(i.fashion_detail.brands.all().values_list('brand', flat=True))])
            else:
                writer.writerow([i.get_full_name() or i.zap_username or "", i.email or "", \
                                 i.phone_number or "", i.profile.sex, i.first_name, "", "", "", ""])
        except:
            pass
    return response

def show(**args):
    args['images'] = "https://zapyle.com" + args['images'][0]
    l = ['commentCount', 'user', 'admired_by_user',
         'upload_time', 'liked_by_user', 'num_products_of_user', 'deletable', 'likesCount']
    # print args
    args["size_id"] = [d['id'] for d in args['size']]
    args["link"] = "https://zapyle.com/product/" + str(args['id']) + "/" + args['description']
    args["seller"] = args["user"]["zap_username"]
    for i in l:
        args.pop(i)
    if args['size_type'] == 'FREESIZE':
        args['size'] = 'FREESIZE'
        args.pop('size_type')
    elif args['size_type'] == '':
        temp = []
        for a in args['size']:
            s = a['us_size']
            temp.append("US" + s)
        args['size'] = "/".join(temp)
        args.pop('size_type')
    else:
        temp = []
        for a in args['no_of_products']:
            sz = a['size_id']
            s = ''
            szg = Size.objects.get(id=sz)
            if args['size_type'] == 'US':
                s = szg.us_size
            if args['size_type'] == 'UK':
                s = szg.uk_size
            if args['size_type'] == 'EU':
                s = szg.eu_size
            temp.append(args['size_type'] + s + "_" + szg.size)
        args['size'] = "/".join(temp)
        args.pop('size_type')
    return args

def export_cart(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="carts.csv"'
    writer = csv.writer(response)
    key = ['username','email','phone','product','id', 'added_at']
    writer.writerow(key)
    for c in Cart.objects.filter(item__isnull=False).distinct('user'):
        for idx, i in enumerate(c.item.all()):
            if idx == 0:
                try:
                    writer.writerow([c.user.username,c.user.email if c.user.email else '',c.user.phone_number if c.user.phone_number else '',i.product.title,i.product.id, i.added_at])
                except UnicodeEncodeError:
                    writer.writerow([c.user.username,c.user.email if c.user.email else '',c.user.phone_number if c.user.phone_number else '','error -- contains emoji',i.product.id, i.added_at])
            else:
                try:
                    writer.writerow(['','','',i.product.title,i.product.id, i.added_at])
                except UnicodeEncodeError:
                    writer.writerow(['','','','error -- contains emoji',i.product.id, added_at])
    return response

def export_product_view(request):
    # if request.GET.get('seller',False):
    #     response = HttpResponse(content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename="products.csv"'
    #     writer = csv.writer(response)
    #     key = ['Email', 'Username', 'Phone', 'Title','id','Listing_Price']
    #     writer.writerow(key)
    #     for i in ZapUser.objects.filter(approved_product__isnull=False).distinct():
    #         for idx, u in enumerate(i.approved_product.all()):
    #             writer.writerow([i.email or "" if idx==0 else "", i.zap_username or "" if idx==0 else "", i.phone_number or "" if idx==0 else "", u.title, u.id,u.listing_price])
    #     return response

    # import os
    # from openpyxl import load_workbook, Workbook
    # directory = settings.HOME_FOLDER + "/frontend/static/export/"
    # if not os.path.exists(directory):
    #     os.makedirs(directory)

    # header = [u'id', u'title', u'original_price', u'listing_price', u'category', u'product_category', u'size', 
    #         u'size_id', u'color', u'listing_price', u'available', u'brand', u'style', u'shop',
    #         u'discount', u'condition', u'age', u'sale', u'sold_out', u'occasion',u'partner_id', 
    #         u'link',u'seller',u'with_zapyle', u'description', u'images']
    # wb = Workbook()

    # dest_filename = directory + "products.xlsx"

    # ws1 = wb.active

    # ws1.title = "products sheet"

    # ws1.append(header)

    # # wb.save(filename = dest_filename)

    # params = request.GET.copy()
   
    # if params:
    #     Q1 = Q()
    #     Q2 = Q()
    #     Q3 = Q()
    #     Q4 = Q()
    #     Q5 = Q()
    #     if params.get('user', False):
    #         Q1 = Q(user__user_type__name__in=[u for u in params['user'].split(',')])
    #     if params.get('from', False):
    #         Q2 = Q(upload_time__gte=params['from'])
    #     if params.get('to', False):
    #         Q3 = Q(upload_time__lte=params['to'])
    #     if params.get('pricefrom', False):
    #         Q4 = Q(listing_price__gte=params['pricefrom'])
    #     if params.get('priceto', False):
    #         Q5 = Q(listing_price__lte=params['priceto'])
    #     # pdb.set_trace()
    #     product = ApprovedProduct.ap_objects.filter(Q1&Q2&Q3&Q4&Q5)
    # else:
    #     product = ApprovedProduct.ap_objects.all()

    # # chunks
    # for c  in range(0, 5000, 100):
    #     srlzed_data = AdminSingleApprovedProducSerializer(product[c:c+100], many = True,
    #                                                       context={'current_user': request.user, 'request': request, 'version':{'version':1}}).data
    #     for i in srlzed_data:
    #         args = show(**i)
    #         l = []
    #         for k in header:
    #             if type(args[k]) == list:
    #                 args[k] = str(args[k])
    #             try:
    #                 l.append(args[k].encode('utf-8'))
    #             except:
    #                 l.append(args[k])
    #         ws1.append(l)
    # wb.save(filename = dest_filename)
    # return HttpResponse("<a href='/zapstatic/export/products.xlsx'><b>Download</b></a><br><br>    <b>Get All Sellers&nbsp</b><a href='/zapadmin/export/products/?seller=true'>/zapadmin/export/products/?seller=true</a><br><br>  <b>Get all Products (listing price from 11000)</b>&nbsp <a href='/zapadmin/export/products/?pricefrom=11000'>/zapadmin/export/products/?pricefrom=11000</a><br><br>  <b>Get all Products (listing price till 50000)</b>&nbsp<a href='/zapadmin/export/products/?priceto=50000'>/zapadmin/export/products/?priceto=50000</a><br><br><b>Get all Products between 2 dates</b>&nbsp<a href='/zapadmin/export/products/?from=2016-12-01&to=2017-03-31'>/zapadmin/export/products/?from=2016-12-01&to=2017-03-31</a><br><br> <b>Get all products (upload date from YYYY-MM-DD)</b>&nbsp<a href='/zapadmin/export/products/?from=2016-12-01'>/zapadmin/export/products/?from=2016-12-01</a><br><br> <b>Get all products (upload date till YYYY-MM-DD)</b>&nbsp;<a href='/zapadmin/export/products/?to=2016-12-01'>/zapadmin/export/products/?to=2016-12-01</a>")
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    if request.GET.get('seller',False):
        key = ['Email', 'Username', 'Phone', 'Title','id','Listing_Price']
        writer.writerow(key)
        for i in ZapUser.objects.filter(approved_product__isnull=False).distinct():
            for idx, u in enumerate(i.approved_product.all()):
                writer.writerow([i.email or "" if idx==0 else "", i.zap_username or "" if idx==0 else "", i.phone_number or "" if idx==0 else "", u.title, u.id,u.listing_price])
        return response

    
    if request.GET.get('seller',False):
        key = ['Email', 'Username', 'Phone', 'Title','id','Listing_Price']
        writer.writerow(key)
        for i in ZapUser.objects.filter(approved_product__isnull=False).distinct():
            for idx, u in enumerate(i.approved_product.all()):
                writer.writerow([i.email or "" if idx==0 else "", i.zap_username or "" if idx==0 else "", i.phone_number or "" if idx==0 else "", u.title, u.id,u.listing_price])
        return response
        return HttpResponse({'status':'sss'})

    params = request.GET.copy()
    if params:
        Q1 = Q()
        Q2 = Q()
        Q3 = Q()
        Q4 = Q()
        Q5 = Q()
        if params.get('user', False):
            Q1 = Q(user__user_type__name__in=[u for u in params['user'].split(',')])
        if params.get('from', False):
            Q2 = Q(upload_time__gte=params['from'])
        if params.get('to', False):
            Q3 = Q(upload_time__lte=params['to'])
        if params.get('pricefrom', False):
            Q4 = Q(listing_price__gte=params['pricefrom'])
        if params.get('priceto', False):
            Q5 = Q(listing_price__lte=params['priceto'])
        # pdb.set_trace()
        product = ApprovedProduct.ap_objects.filter(Q1&Q2&Q3&Q4&Q5)
    else:
        product = ApprovedProduct.ap_objects.all()
    key = ['id', 'title', 'original_price', 'listing_price', 'category', 'product_category', 'size', 
            'size_id', 'color', 'listing_price', 'available', 'brand', 'style', 'shop',
            'discount', 'condition', 'age', 'sale', 'sold_out', 'occasion','partner_id', 
            'link','seller','with_zapyle', 'description', 'images', 'percentage_commission']
    writer.writerow(key)
    # chunks
    for c  in range(0, 5000, 100):
        srlzed_data = AdminSingleApprovedProducSerializer(product[c:c+100], many = True,
                                                          context={'current_user': request.user, 'request': request, 'version':{'version':1}}).data
        for i in srlzed_data:
            args = show(**i)
            l = []
            for k in key:
                try:
                    l.append(args[k].encode('utf-8'))
                except:
                    l.append(args[k])

            writer.writerow(l)
    return response


    for i in product:
        # srlzr = AndroidSingleApprovedProducSerializer(i,
        #    
        srlzr = AdminSingleApprovedProducSerializer(i,
                                                      context={'current_user': request.user, 'request': request, 'version':{'version':1}})
        # # Create the HttpResponse object with the appropriate CSV header.
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
        # writer = csv.writer(response)
        # writer.writerow(['Name', 'Email','Phone','Joined'])
        # p = datetime.date(2016, 3, 16)
        # for i in ZapUser.objects.filter(logged_device__name='website').exclude(date_joined__startswith=p):
        #     try:
        #         writer.writerow([i.get_full_name() or i.zap_username or "", i.email or "",i.phone_number or "",i.date_joined])
        #     except:
        #         pass
        args = show(**srlzr.data)
        l = []
        for k in key:
            try:
                l.append(args[k].encode('utf-8'))
            except:
                l.append(args[k])

        writer.writerow(l)
    return response

@api_view(['GET', 'POST', ])
def export_item_count(request, item):
    params = request.GET.copy()
    Q1 = Q()
    Q2 = Q()
    Q3 = Q()
    if params.get('user', False):
        Q1 = Q(user__user_type__name__in=[u for u in params['user'].split(',')])
    if params.get('from', False):
        Q2 = Q(upload_time__gte=params['from'])
    if params.get('to', False):
        Q3 = Q(upload_time__lte=params['to'])
    # return Response({'status' : 'error'})
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="carts.csv"'
    writer = csv.writer(response)
    if item == 'brand':
        if params.get('bydate', False):
            key = ['date', 'brand','no_of_products']
            writer.writerow(key)
            query = ApprovedProduct.ap_objects.filter(Q1&Q2)
            for i in Counter([dt.date() for dt in query.values_list('upload_time', flat=True)]):
                count_list = ApprovedProduct.ap_objects.filter(upload_time__date=i).values_list('brand__brand',flat=True)
                dicts = Counter(count_list)
                for idx, b in enumerate(dicts):
                    if idx == 0:
                        writer.writerow([i, b.encode("utf-8"), dicts[b]])
                    else:
                        writer.writerow(['', b.encode("utf-8"), dicts[b]])
            return response
        else:
            key = ['brand','no_of_products']
            writer.writerow(key)
            count_list = ApprovedProduct.ap_objects.filter(Q1&Q2).values_list('brand__brand',flat=True)
    elif item == 'subcategory':
        if params.get('bydate', False):
            key = ['date', 'subcategory','no_of_products']
            writer.writerow(key)
            query = ApprovedProduct.ap_objects.filter(Q1&Q2)
            for i in Counter([dt.date() for dt in query.values_list('upload_time', flat=True)]):
                count_list = ApprovedProduct.ap_objects.filter(upload_time__date=i).values_list('product_category__name',flat=True)
                dicts = Counter(count_list)
                for idx, b in enumerate(dicts):
                    if idx == 0:
                        writer.writerow([i, b, dicts[b]])
                    else:
                        writer.writerow(['', b, dicts[b]])
            return response
        else:
            key = ['subcategory','no_of_products']
            writer.writerow(key)
            count_list = ApprovedProduct.ap_objects.filter(Q1&Q2).values_list('product_category__name',flat=True)
    elif item == 'category':
        if params.get('bydate', False):
            key = ['date', 'category','no_of_products']
            writer.writerow(key)
            query = ApprovedProduct.ap_objects.filter(Q1&Q2)
            for i in Counter([dt.date() for dt in query.values_list('upload_time', flat=True)]):
                count_list = ApprovedProduct.ap_objects.filter(upload_time__date=i).values_list('product_category__parent__name',flat=True)
                dicts = Counter(count_list)
                for idx, b in enumerate(dicts):
                    if idx == 0:
                        writer.writerow([i, b, dicts[b]])
                    else:
                        writer.writerow(['', b, dicts[b]])
            return response
        else:
            key = ['category', 'no_of_products']
            writer.writerow(key)
            count_list = ApprovedProduct.ap_objects.filter(Q1&Q2).values_list('product_category__parent__name',flat=True)
    dicts = Counter(count_list)
    for b in dicts:
        writer.writerow([b, dicts[b]])
    return response

@api_view(['GET', 'POST', ])
def export_amazon(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="name_email.csv"'
    writer = csv.writer(response)
    writer.writerow(['Recommended Browse Nodes','Seller SKU','Product ID','Product ID Type','Item Name (aka Title)','Brand Name','Product Sub-type','Manufacturer Part Number','Manufacturer','Item Length','Style Name','Colour','Department','Size','Colour Map','Size Map','Material type','Collection Description','Standard Price','Quantity','Main Image URL','Other Image URL','Other Image URL','Other Image URL','Swatch Image URL','Parentage','Parent SKU','Relationship Type','Variation Theme','Product Description','Update Delete','Search Terms','Search Terms','Search Terms','Search Terms','Search Terms','Key Product Features','Key Product Features','Key Product Features','Key Product Features','Key Product Features','Shipping Weight','Website Shipping Weight Unit Of Measure','Item Weight','Item Weight Unit of Measure','Legal Disclaimer Description','Safety Warning','Country Of Origin','Country String','Condition','Condition Note','Fulfillment Latency','Sale Price','Sale Start Date','Sale End Date','Package Quantity','Number of Items','Can Be Gift Messaged','Is Gift Wrap Available?','Launch Date','Restock Date','Product Tax Code'])
    writer.writerow([
        'recommended_browse_nodes', 
        'item_sku',
        'external_product_id',
        'external_product_id_type',
        'item_name',
        'brand_name',
        'product_subtype',
        'part_number',
        'manufacturer',
        'item_length_description',
        'style_name',
        'color_name',
        'department_name',
        'size_name',
        'color_map',
        'size_map',
        'material_type',
        'collection_description',
        'standard_price',
        'quantity',
        'main_image_url',
        'other_image_url1',
        'other_image_url2',
        'other_image_url3',
        'swatch_image_url',
        'parent_child',
        'parent_sku',
        'relationship_type',
        'variation_theme',
        'product_description',
        'update_delete',
        'generic_keywords1',
        'generic_keywords2',
        'generic_keywords3',
        'generic_keywords4',
        'generic_keywords5',
        'bullet_point1',
        'bullet_point2',
        'bullet_point3',
        'bullet_point4',
        'bullet_point5',
        'website_shipping_weight',
        'website_shipping_weight_unit_of_measure',
        'item_weight',
        'item_weight_unit_of_measure',
        'legal_disclaimer_description',
        'safety_warning',
        'country_of_origin',
        'country_string',
        'condition_type',
        'condition_note',
        'fulfillment_latency',
        'sale_price',
        'sale_from_date',
        'sale_end_date',
        'item_package_quantity',
        'number_of_items',
        'offering_can_be_gift_messaged',
        'offering_can_be_giftwrapped',
        'product_site_launch_date',
        'restock_date',
        'product_tax_code'

    ])

    try:
        for p in ApprovedProduct.ap_objects.filter(user__representing_brand__designer_brand=True, user__user_type__name='designer',product_category__name__in=['Dresses','Sari','Lehenga','Kurta']):
            img = p.images.all()
            img_count = img.count()
            parent = "ZAP{}S{}".format(p.id,p.user.id)
            if p.product_count.count() == 1:
                writer.writerow([
                    "1968255031",#recommended_browse_nodes'
                    parent,#item_sku
                    p.id,#external_product_id
                    "ASIN",#external_product_id_type
                    p.title,
                    p.brand.brand,#brand_name
                    "Ethnicwear",#product_subtype
                    "",#part_number
                    p.brand.brand,#manufacturer
                    "",#item_length_description
                    p.style.style_type if p.style else "",
                    p.color.name if p.color else "",#color_name
                    "Women",#department_name
                    "",#size_name
                    "",#color_map
                    "",#size_map
                    "",#material_type
                    "Designer",#collection_description
                    p.original_price,#standard_price
                    p.product_count.first().quantity,#quantity
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[0]) if img_count > 0 else "",#main_image_url
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[1]) if img_count > 1 else "",#other_image_url1
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[2]) if img_count > 2 else "",#other_image_url2
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[3]) if img_count > 3 else "",#other_image_url3
                    "",#swatch_image_ur
                    "",#parent_child
                    "",#parent_sku
                    "",#relationship_type
                    "",#variation_theme
                    p.description,#product_description
                    "",#update_delete
                    "",#generic_keywords1
                    "",#generic_keywords2
                    "",#generic_keywords3
                    "",#generic_keywords4
                    "",#generic_keywords5
                    "",#bullet_point1
                    "",#bullet_point2
                    "",#bullet_point3'
                    "",#bullet_point4'
                    "",#bullet_point5'
                    "",#website_shipping_weight'
                    "",#website_shipping_weight_unit_of_measure'
                    "",#item_weight'
                    "",#item_weight_unit_of_measure'
                    "",#legal_disclaimer_description'
                    "",#safety_warning'
                    "India",#country_of_origin'
                    "India",#country_string'
                    p.get_condition_display(),#condition_type'
                    "",#condition_note'
                    "",#fulfillment_latency
                    p.listing_price,#sale_price
                    "",#sale_from_date
                    "",#sale_end_date
                    "",#item_package_quantity
                    "",#number_of_items
                    "",#offering_can_be_gift_messaged
                    "",#offering_can_be_giftwrapped
                    "",#product_site_launch_date
                    "",#restock_date
                    "",#product_tax_cod
                ])
            else:
                writer.writerow([
                    "1968255031",#recommended_browse_nodes'
                    "ZAP{}S{}".format(p.id,p.user.id),#item_sku
                    "",#external_product_id
                    "",#external_product_id_type
                    p.title,
                    p.brand.brand,#brand_name
                    "Ethnicwear",#product_subtype
                    "",#part_number
                    p.brand.brand,#manufacturer
                    "",#item_length_description
                    p.style.style_type if p.style else "",
                    p.color.name if p.color else "",#color_name
                    "Women",#department_name
                    "",#size_name
                    "",#color_map
                    "",#size_map
                    "",#material_type
                    "Designer",#collection_description
                    p.original_price,#standard_price
                    "",#quantity
                    "",#main_image_url
                    "",#other_image_url1
                    "",#other_image_url2
                    "",#other_image_url3
                    "",#swatch_image_ur
                    "Parent",#parent_child
                    "",#parent_sku
                    "",#relationship_type
                    "",#variation_theme
                    p.description,#product_description
                    "",#update_delete
                    "",#generic_keywords1
                    "",#generic_keywords2
                    "",#generic_keywords3
                    "",#generic_keywords4
                    "",#generic_keywords5
                    "",#bullet_point1
                    "",#bullet_point2
                    "",#bullet_point3'
                    "",#bullet_point4'
                    "",#bullet_point5'
                    "",#website_shipping_weight'
                    "",#website_shipping_weight_unit_of_measure'
                    "",#item_weight'
                    "",#item_weight_unit_of_measure'
                    "",#legal_disclaimer_description'
                    "",#safety_warning'
                    "India",#country_of_origin'
                    "India",#country_string'
                    p.get_condition_display(),#condition_type'
                    "",#condition_note'
                    "",#fulfillment_latency
                    p.listing_price,#sale_price
                    "",#sale_from_date
                    "",#sale_end_date
                    "",#item_package_quantity
                    "",#number_of_items
                    "",#offering_can_be_gift_messaged
                    "",#offering_can_be_giftwrapped
                    "",#product_site_launch_date
                    "",#restock_date
                    "",#product_tax_cod
                ])
                for i in p.product_count.all():
                    writer.writerow([
                    "1968255031",#recommended_browse_nodes'
                    "ZAP{}S{}-{}".format(p.id,p.user.id,i.id),#item_sku
                    p.id,#external_product_id
                    "ASIN",#external_product_id_type
                    p.title,
                    p.brand.brand,#brand_name
                    "Ethnicwear",#product_subtype
                    "",#part_number
                    p.brand.brand,#manufacturer
                    "",#item_length_description
                    p.style.style_type if p.style else "",
                    p.color.name if p.color else "",#color_name
                    "Women",#department_name
                    "",#size_name
                    "",#color_map
                    "",#size_map
                    "",#material_type
                    "Designer",#collection_description
                    p.original_price,#standard_price
                    i.quantity,#quantity
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[0]) if img_count > 0 else "",#main_image_url
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[1]) if img_count > 1 else "",#other_image_url1
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[2]) if img_count > 2 else "",#other_image_url2
                    settings.CURRENT_DOMAIN+'/zapmedia/'+str(img[3]) if img_count > 3 else "",#other_image_url3
                    "",#swatch_image_ur
                    "Child",#parent_child
                    parent,#parent_sku
                    "Variation",#relationship_type
                    "",#variation_theme
                    p.description,#product_description
                    "",#update_delete
                    "",#generic_keywords1
                    "",#generic_keywords2
                    "",#generic_keywords3
                    "",#generic_keywords4
                    "",#generic_keywords5
                    "",#bullet_point1
                    "",#bullet_point2
                    "",#bullet_point3'
                    "",#bullet_point4'
                    "",#bullet_point5'
                    "",#website_shipping_weight'
                    "",#website_shipping_weight_unit_of_measure'
                    "",#item_weight'
                    "",#item_weight_unit_of_measure'
                    "",#legal_disclaimer_description'
                    "",#safety_warning'
                    "India",#country_of_origin'
                    "India",#country_string'
                    p.get_condition_display(),#condition_type'
                    "",#condition_note'
                    "",#fulfillment_latency
                    p.listing_price,#sale_price
                    "",#sale_from_date
                    "",#sale_end_date
                    "",#item_package_quantity
                    "",#number_of_items
                    "",#offering_can_be_gift_messaged
                    "",#offering_can_be_giftwrapped
                    "",#product_site_launch_date
                    "",#restock_date
                    "",#product_tax_cod
                ])
        return response
    except Exception as e:
        return Response({'error': str(e), 'product': p.id})


class MarketingImageForm(forms.Form):
    image = forms.FileField(label='Select a file',)
@api_view(['GET', 'POST', ])
@admin_only
def marketing_notification(request):
    # pdb.set_trace()
    data = request.data
    print data,'-------------'
    # if not 'action_type' in data:
    #     return Response({'status': 'error','detail':'Action is missing.'})
    if 'action_type' in data and data['action_type'] in ['profile','product','filtered']:
        data['data'] = ast.literal_eval(data['data']) #convert action data to dictionary
    if 'action_type' in data and data['action_type'] in ['profile','product'] and not data['data']['id']:
        return Response({'status': 'error','detail':'Action data is missing.'})

    data['image'] = None
    if data['time'] and not 'true' in data['clevertap']:
        try:
            data['time'] = datetime.datetime.strptime(data['time'], '%Y/%m/%d %I:%M %p')
            current_time = datetime.datetime.now()
            time_minus_5_30 = data['time'] - timedelta(days=0, hours=5, minutes=35)
            time_diff = time_minus_5_30 - current_time
            if not time_diff.total_seconds() > 300:
                return Response({'status' : 'error','detail':'Time expired.'})
        except ValueError:
            return Response({'status': 'error','detail':'Invalid time. (format: YYY/MM/DD HH:MM AM/PM)'})
    if request.FILES:
        form = MarketingImageForm(request.data, request.FILES)
        if form.is_valid():
            data['image'] = request.FILES['image']
            # new_image = MarketingImage(image = request.FILES['image'])
            # new_image.save()
            # data['image'] = new_image.image.url
        else:
            return Response({'status': 'error','detail':'invalid image'})
    if 'true' in data['clevertap']:
        data['text'] = 'clevertap'
    srlzr = ActionSerializer(data=data)
    if srlzr.is_valid():
        srlzr.save()
        data['action'] = srlzr.data['id']
    else:
        print srlzr.errors,' srlzr.errors'
        return Response({'status': 'error', 'detail':srlzr.errors})
    srlzr = NotifsSerializer(data=data)
    if srlzr.is_valid():
        notif = srlzr.save()
    else:
        return Response({'status': 'error', 'detail':srlzr.errors})

    if 'true' in data.get('ctap',[]):
        json_data = get_json_for_push_notification(notif)
        resp = clevertap_push_notification(json_data, data, notif)
        print resp,' resp'
        if "success" in resp:
            return Response({'status' : 'success'})
        else:
            return Response({'status' : 'error'})

    if 'true' in data['clevertap']:
        data = get_json_for_push_notification(notif)
        json_data = {
            "branch_key": "key_live_ldkXgZOU0rwWtmErlwGMymcpqDkFdsZ9",
            "sdk" : "api",
            "data" : data
        }
        url = "https://api.branch.io/v1/url"
        headers = {'Content-Type': 'application/json'}
        branch_data = json.dumps(json_data)
        resp = requests.post(url, headers=headers, data=branch_data)
        json_response = resp.json()
        try:
            branch_url = json_response['url']
        except KeyError:
            branch_url = json_response['error']['message']
        return Response({'status':'success','json_data':data, 'branch_url':branch_url})
    if data['type'] == 'AllUsers':
        users = ZapUser.objects.all()
    elif data['type'] == 'zapyleTeam':
        users = ZapUser.objects.filter(email__in=['shafi374@gmail.com','bhargavkanda@gmail.com','sundeepreddy10@gmail.com','sk@gmail.com','Rashigulati003@gmail.com','rashi@zapyle.com','haseeb@zapyle.com','rajeesh@gmail.com','likhita.nimmagadda@gmail.com','freda.pinto.gaia@gmail.com','m.ruby92@gmail.com'])
    elif data['type'] == 'iosUsers':
        users = ZapUser.objects.filter(logged_device__name="ios")
    elif data['type'] == 'androidUsers':
        users = ZapUser.objects.filter(logged_device__name="android")
    else:
        u = ast.literal_eval(data['users'])
        if type(u) == tuple:
            data['users'] = list(u)  #unicode to list
        users = ZapUser.objects.filter(id__in=data['users'])

    if data['time']:
        current_time = datetime.datetime.now()
        time_minus_5_30 = data['time'] - timedelta(days=0, hours=5, minutes=35)
        time_diff = time_minus_5_30 - current_time
        if time_diff.total_seconds() > 300:
            marketing_send_notif.apply_async(args=[notif, users], eta=time_minus_5_30)
        else:
            return Response({'status' : 'error','detail':'Invalid time or Time expired.'})
    else:
        marketing_send_notif.delay(notif, users)       
    return Response({'status': 'success'})


@api_view(['GET', 'POST', ])
@admin_only
def get_brand_products(request):
    # pdb.set_trace()
    params = request.GET
    print params.get('type')
    if params.get('segment') == 'curated':
        data = [{'id':p.id,'title':p.title} for p in ApprovedProduct.objects.filter(brand__brand=params.get('brand'),status='1',user__user_type__name='zap_exclusive')] 
    elif params.get('segment') == 'market':
        data = [{'id':p.id,'title':p.title} for p in ApprovedProduct.objects.filter(brand__brand=params.get('brand'),status='1',user__user_type__name__in=['zap_user','zap_dummy', 'store_front'])] 
    elif params.get('segment') == 'approved':
        data = [{'id':p.id,'title':p.title} for p in ApprovedProduct.objects.filter(brand__brand=params.get('brand'),status='1')]     
    elif params.get('segment') == 'tobeapproved':
        data = [{'id':p.id,'title':p.title} for p in ApprovedProduct.objects.filter(brand__brand=params.get('brand'),status='0')]     
    elif params.get('segment') == 'disaapproved':
        data = [{'id':p.id,'title':p.title} for p in ApprovedProduct.objects.filter(brand__brand=params.get('brand'),status='2')]     
    else:   
        data = [{'id':p.id,'title':p.title} for p in ApprovedProduct.objects.filter(brand__brand=params.get('brand'))]
    return Response({'status': 'success','data':data})

@api_view(['GET', 'POST', ])
@admin_only
def track_logistics_status(request):
    params = request.data.copy()  
    print params
    data = {"status1":"Data Not Available"}  
    if params['status'] in ['pickup_in_process', 'return_in_process', 'picked_up']:
        log = LogisticsLog.objects.get(pickup=True, logistics__orders=params['order_id'])
        data = track_order(log.id, log.partner)
    elif params['status'] in ['product_approved', 'on_the_way_to_you', 'delivered', 'verification']:
        log = LogisticsLog.objects.get(pickup=False, logistics__orders=params['order_id'])
        data = track_order(log.id, log.partner)

    return Response({'status':'success', 'data':data})
