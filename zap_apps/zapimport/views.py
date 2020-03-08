from django.shortcuts import render
from django.utils.crypto import get_random_string
from zap_apps.account.zapauth import ZapView, ZapAuthView
import re
import time
import random
from zap_apps.zapuser.models import ZapUser
from zap_apps.zapuser.models import LoggedFrom, ZapRole, UserProfile, UserData
from zap_apps.zap_catalogue.product_serializer import AndroidProductsToApproveSerializer, NumberOfProductSrlzr
from zap_apps.zap_catalogue.product_serializer import ProductImageSerializer
from zap_apps.zap_catalogue.models import (Comments, ApprovedProduct, Size, NumberOfProducts, 
    Brand, Occasion, Category, Color, Loves,SubCategory, ProductImage, Style)
from zap_apps.zap_upload.upload_serializer import GetApprovedProductStep1, GetApprovedProductStep2, GetApprovedProductStep3, UpdateApprovedProductSerializerAndroid
from zap_apps.address.models import Address, State
from zap_apps.coupon.models import Coupon
from zap_apps.cart.models import Item, Cart
from zap_apps.order.models import Transaction, Order, Return
from zap_apps.payment.models import PaymentResponse
from zap_apps.logistics.models import Logistics


class ZapImportHandler(ZapView):
    def post(self, request, format=None):
        print request.data.copy()
        if request.GET.get('action') == 'create_user':
            data = request.data.copy()
            try:
                u = ZapUser.objects.get(id=data.get('id'))
            except ZapUser.DoesNotExist:
                try:
                    if data.get('email'):
                        u = ZapUser.objects.get(email=data.get('email'))
                    else:
                        raise ZapUser.DoesNotExist
                except ZapUser.DoesNotExist:
                    try:
                        if data.get('username'):
                            u = ZapUser.objects.get(fb_id=data['username'])
                        else:
                            raise ZapUser.DoesNotExist
                    except ZapUser.DoesNotExist:
                        u = ZapUser(id=data.get('id'))
            if data.get('logged_from') == 'fb':
                u.fb_id = data['username']
                u.logged_from = LoggedFrom.objects.get(name="fb")
            if data.get('logged_from') == 'insta':
                u.username = data['username']
                u.logged_from = LoggedFrom.objects.get(name="instagram")
            u.zap_username = data.get('zap_username')
            u.phone_number = data.get('phone_number')
            if data.get('user_type') == 'store_front':
                u.user_type = ZapRole.objects.get(name="store_front")
            if data.get('user_type') == 'normal':
                u.user_type = ZapRole.objects.get(name="zap_user")
            u.pushBotToken = data.get('pushBotToken')
            # u.email = data.get('email') or "testmail"+get_random_string(10)+'@gmail.com'
            u.email = data.get('email') or ""
            try:
                u.first_name = data['full_name'].split()[0]
                u.last_name = data['full_name'].split()[1]
            except:
                pass
            if not u.username:
                u.username = get_random_string(10)
            u.save()
            UserProfile.objects.get_or_create(user=u)
            UserData.objects.get_or_create(user=u)
        if request.GET.get('action') == 'admire':
          data = request.data.copy()
          user = ZapUser.objects.get(id=data.get('user'))
          if data['admirers']:
            user.profile.admiring.add(*[ZapUser.objects.get(id=i).id for i in data['admirers']])
          user.profile.save()
        if request.GET.get('action') == 'profile':
          data = request.data.copy()
          user = ZapUser.objects.get(id=data['user'])
          user.profile.description = data['data'].get('description')
          user.profile.profile_pic = data['data'].get('profile_pic')
          user.profile.zap_score = data['data'].get('zap_score')
          user.profile.normalized_zap_score = data['data'].get('normalized_zap_score')
          user.profile.save()
        if request.GET.get('action') == 'user_data':
          data = request.data.copy()
          user = ZapUser.objects.get(id=data['user'])
          user.user_data.account_number = data['data'].get('new_account_number')
          user.user_data.old_account_number = data['data'].get('account_number')
          user.user_data.ifsc_code = data['data'].get('new_ifsc_code')
          user.user_data.old_ifsc_code = data['data'].get('ifsc_code')
          user.user_data.save()
        if request.GET.get('action') == 'address':
            data = request.data.copy()
            user = ZapUser.objects.get(id=data['user'])
            a = Address(id=data['data'].get('id'))
            a.user=user
            a.address = data['data'].get('address')
            a.name = data['data'].get('name')
            a.city = data['data'].get('city')
            try:
                a.state = State.objects.get(name__icontains=data['data'].get('state'))
            except State.MultipleObjectsReturned:
                a.state = State.objects.filter(name__icontains=data['data'].get('state'))[0]
            except State.DoesNotExist:
                a.state = State.objects.first()

            a.phone = data['data'].get('phone')
            a.pincode = data['data'].get('pincode')
            a.save()
        if request.GET.get('action') == 'product':
            data = request.data.copy()
            user = ZapUser.objects.get(id=data['user'])
            if data['data'].get('approved') == '-1':
                p = DisapprovedProduct(id=data['data'].get('id'))
                p.disapproved_reason = data['data'].get('disapproved_reason')
            if data['data'].get('approved') == '0':
                p = ProductsToApprove(id=data['data'].get('id'))
            if data['data'].get('approved') == '1':
                p = ApprovedProduct(id=data['data'].get('id'))
            p.user=user
            p.description = data['data'].get('description')
            p.original_price = data['data'].get('original_price')
            p.listing_price = data['data'].get('listing_price')
            p.description = data['data'].get('description')
            p.title = data['data'].get('album_title')
            p.pickup_address_id = data['data'].get('pickup_address_id')
            p.brand, c = Brand.objects.get_or_create(brand=data['data'].get('brand'))
            p.upload_time = data['data'].get('upload_time')
            p.sale = data['data'].get('sale') if data['data'].get('sale') in ['1', '2'] else '2'
            p.occasion = Occasion.objects.get(name=data['data'].get('occasion'))
            p.product_category = SubCategory.objects.get(name=data['data'].get('product_category'))
            try:
                p.style = Style.objects.get(style_type=data['data'].get('fashion_type'))
            except:
                pass
            if data['data'].get('color'):
                p.color = Color.objects.get(name=data['data'].get('color'))
            p.completed = data['data'].get('completed')
            p.age = data['data'].get('age')
            p.condition = data['data'].get('condition')
            p.discount =  data['data'].get('discount')
            p.save()
        if request.GET.get('action') == 'love':
            data = request.data.copy()
            l = Loves(id=data['id'])
            l.loved_by = ZapUser.objects.get(id=data['liked_by_id'])
            try:
                l.product = ApprovedProduct.objects.get(id=data['album_id'])
            except ApprovedProduct.DoesNotExist:
                pass
                # try:
                #     l.product = ProductsToApprove.objects.get(id=data['album_id'])
                # except ProductsToApprove.DoesNotExist:
                #     l.product = DisapprovedProduct.objects.get(id=data['album_id'])
            l.save()        
        if request.GET.get('action') == 'comment':
            data = request.data.copy()
            c = Comments(id=data['id'])
            c.product_id = data['album_id']
            c.commented_by = ZapUser.objects.get(id=data['commented_by_id'])
            c.comment = data.get('comment')
            c.comment_time = data.get('comment_time')
            c.save()
        if request.GET.get('action') == 'image':
            p_id = request.data['product_id']
            image = request.FILES['image']
            try:
                p = ProductImage.objects.get(id=request.data['image_id'])
            except ProductImage.DoesNotExist:
                p = ProductImage(id=request.data['image_id'])
                p.image = image
                p.save()
            try:
                a = ApprovedProduct.objects.get(id=p_id)
            except ApprovedProduct.DoesNotExist:
                try:
                    a = ProductsToApprove.objects.get(id=p_id)
                except ProductsToApprove.DoesNotExist:
                    a = DisapprovedProduct.objects.get(id=p_id)
            a.images.add(p)
        if request.GET.get('action') == 'size':
            p_id = request.data['album_id']
            approved = request.data['album__approved']
            if approved == '0':
                n = NumberOfProducts(id=request.data['id'])
                n.product_to_approve_id=p_id
                n.quantity = request.data['quantity']
                ProductsToApprove.objects.filter(id=p_id).update(size_type=request.data.get('size__size_type') or 'FREESIZE')
            if approved == '1':
                n = NumberOfProducts(id=request.data['id'])
                n.product_id=p_id
                n.quantity = request.data['quantity']
                ApprovedProduct.ap_objects.filter(id=p_id).update(size_type=request.data.get('size__size_type') or 'FREESIZE')
            if approved == '-1':
                n = NumberOfProducts(id=request.data['id'])
                n.disapproved_product_id=p_id
                n.quantity = request.data['quantity']
                DisapprovedProduct.objects.filter(id=p_id).update(size_type=request.data.get('size__size_type') or 'FREESIZE')
            if request.data['size__size_type'] == 'UK':
                try:
                    s = Size.objects.get(uk_size=request.data['size__size'])
                    n.size_id = s.id
                except Size.DoesNotExist:
                    print "No size for UK-{}".format(request.data['size__size'])
                    try:
                        s = Size.objects.get(uk_size=str(float(request.data['size__size'])))
                        n.size_id = s.id
                    except Size.DoesNotExist:
                        s = Size.objects.get(uk_size=str(int(request.data['size__size'])+1))
                        n.size_id = s.id                        
                    except:
                        print "Cannot add size UK-{} <<<<<<>>>>>>".format(request.data['size__size'])
                except Size.MultipleObjectsReturned:
                    s = Size.objects.filter(uk_size=request.data['size__size'])[0]
                    n.size_id = s.id
            if request.data['size__size_type'] == 'US':
                try:
                    s = Size.objects.get(us_size=request.data['size__size'])
                    n.size_id = s.id
                except Size.DoesNotExist:
                    print "No size for US-{}".format(request.data['size__size'])
                    try:
                        s = Size.objects.get(us_size=str(float(request.data['size__size'])))
                        n.size_id = s.id
                    except Size.DoesNotExist:
                        s = Size.objects.get(us_size=str(int(request.data['size__size'])+1))
                        n.size_id = s.id 
                    except:
                        print "Cannot add size US-{} <<<<<<>>>>>>".format(request.data['size__size'])
                except Size.MultipleObjectsReturned:
                    s = Size.objects.filter(us_size=request.data['size__size'])[0]
                    n.size_id = s.id
            if request.data['size__size_type'] == 'EU':
                try:
                    s = Size.objects.get(eu_size=request.data['size__size'])
                    n.size_id = s.id
                except Size.DoesNotExist:
                    print "No size for EU-{}".format(request.data['size__size'])
                    try:
                        s = Size.objects.get(eu_size=str(float(request.data['size__size'])))
                        n.size_id = s.id
                    except Size.DoesNotExist:
                        s = Size.objects.get(eu_size=str(int(request.data['size__size'])+1))
                        n.size_id = s.id 
                    except:
                        print "Cannot add size EU-{} <<<<<<>>>>>>".format(request.data['size__size'])
                except Size.MultipleObjectsReturned:
                    s = Size.objects.filter(eu_size=request.data['size__size'])[0]
                    n.size_id = s.id
            if request.data['size__size_type'] == '':
                try:
                    s = Size.objects.get(eu_size=request.data['size__size'])
                    n.size_id = s.id
                except Size.DoesNotExist:
                    print "No size for EU-{}".format(request.data['size__size'])
                    try:
                        s = Size.objects.get(eu_size=str(float(request.data['size__size'])))
                        n.size_id = s.id
                    except:
                        print "Cannot add size EU-{} <<<<<<>>>>>>".format(request.data['size__size'])
                except Size.MultipleObjectsReturned:
                    s = Size.objects.filter(eu_size=request.data['size__size'])[0]
                    n.size_id = s.id
            if request.data['size__size_type'] == "":
                s = Size.objects.get(category_type="FS")
                n.size_id = s.id             
            n.save()              

        if request.GET.get('action') == 'coupon':
            data = request.data.copy()
            c = Coupon(id=data.get('id'))
            c.coupon_code = data.get('coupon_code')
            c.coupon_description = data.get('description')
            c.perc_discount = data.get('perc_discount')
            c.abs_discount = data.get('abs_discount')
            c.max_discount = data.get('max_discount')
            c.valid_from = data.get('valid_from')
            c.valid_till = data.get('valid_till')
            c.min_purchase = data.get('min_purchase')
            c.save()
            
        if request.GET.get('action') == 'order':
            data = request.data.copy()
            try:
                ApprovedProduct.objects.get(id=data.get('product_id'))
            except ApprovedProduct.DoesNotExist:
                print 'product not found : ',data.get('product_id')
                return self.send_response(0, "Error.")

            s = data.get('size')['size_type']
            if s == 'US':
                try:
                    size_obj = Size.objects.get(us_size=data.get('size')['size'])
                except Size.DoesNotExist:
                    size_obj = Size.objects.get(us_size=str(int(data.get('size')['size'])+1))
            elif s == 'UK':
                try:
                    size_obj = Size.objects.get(uk_size=data.get('size')['size'])
                except Size.DoesNotExist:
                    size_obj = Size.objects.get(uk_size=str(int(data.get('size')['size'])+1))
            elif s == 'EU':
                try:
                    size_obj = Size.objects.get(eu_size=data.get('size')['size'])
                except Size.DoesNotExist:
                    size_obj = Size.objects.get(eu_size=str(int(data.get('size')['size'])+1))
            else:
                size_obj = Size.objects.get(category_type="FS")
            i = Item()
            i.product_id = data.get('product_id')
            i.size = size_obj
            i.quantity = data.get('quantity')
            i.price = data.get('transaction')['total_price']
            i.added_at = data.get('transaction')['time']
            i.save()
            c = Cart()
            c.user_id = data.get('transaction')['buyer_id']
            c.coupon_id = data.get('transaction')['coupon_id']
            c.delivery_address_id = data.get('transaction')['delivery_address_id']
            c.shipping_charge = 0
            c.success = True
            c.save()
            c.items.add(i)
            t = Transaction(id=data.get('id'))
            t.cart = c
            t.buyer_id = data.get('transaction')['buyer_id']
            t.listing_price_sum = data.get('transaction')['total_price'] * data.get('quantity')
            t.total_price = data.get('transaction')['final_price']
            t.final_price = data.get('transaction')['final_price']
            t.total_discount = data.get('transaction')['total_price'] - data.get('transaction')['final_price']
            t.zapcash_used = 0 #set it to zero
            t.time = data.get('transaction')['time']
            t.success = data.get('transaction')['success']
            # t.initiate_payout = ***
            t.paid_out = data.get('paid_out')
            t.cod = data.get('cod')
            t.transaction_ref = str(int(time.time())) + str(random.randint(10000, 99999))
            t.success = True
            t.save()
            order_number = "OD" + "%.3f" % round(time.time(), 3)
            order_number = order_number.replace('.', '')
            o = Order(id=data.get('id'))
            o.transaction = t
            o.order_number = order_number
            o.product_id = data.get('product_id')
            o.quantity = data.get('quantity')
            o.cancelled = data.get('cancelled')
            o.returned = data.get('returned')
            o.consignee_id = data.get('consignee_id')
            o.consignor_id = data.get('consignor_id')
            o.total_price = data.get('transaction')['total_price']
            o.final_price = data.get('transaction')['final_price']
            o.delivery_date = data.get('delivery_date')
            o.confirmed_with_buyer = True#data.get('confirmed_with_buyer')
            o.confirmed_with_seller = True#data.get('confirmed_with_seller')
            o.placed_at = data.get('placed_at')
            o.triggered_logistics = data.get('triggered_logistics')
            o.size = size_obj
            # o.service_invoice_no
            o.save() 

        if request.GET.get('action') == 'return':
            data = request.data.copy()
            r = Return(id=data['data'].get('id'))
            r.order_id = data['data'].get('order_id')
            r.reason = data['data'].get('reason')
            r.consignee = data['data'].get('consignee')
            r.consignor = data['data'].get('consignor')
            r.delivery_date = data['data'].get('order_id')
            r.value = data['data'].get('value')
            r.requested_at = data['data'].get('requested_at')
            # r.approved_zapcash = 
            r.approved = data['data'].get('approved')
            r.credited = data['data'].get('credited')
            # r.self_return = 
            r.triggered_logistics = data['data'].get('triggered_logistics')
            r.save()
        # we have no cancellation model #
        if request.GET.get('action') == 'logistics':
            data = request.data.copy()
            l = Logistics(id=data['data'].get('id'))
            l.orders = data['data'].get('orders')
            l.returns = data['data'].get('returns')
            l.confirmed_at = data['data'].get('confirmed_at')
            l.consignee = data['data'].get('consignee')
            l.consignor = data['data'].get('consignor')
            # l.packaging_material_delivered = 
            # l.triggered_packaging_material = 
            l.status = data['data'].get('status')
            # l.delivery_time = 
            # l.packaging_material_partner = 
            # l.product_delivery_partner = 
            l.save()
        if request.GET.get('action') == 'paymentResponse':
            data = request.data.copy()
            p = PaymentResponse(id=data['data'].get('id'))
            p.transaction = data['data'].get('transaction')
            p.payment_success = data['data'].get('payment_success')
            p.payment_id = data['data'].get('payment_id')
            p.payment_transaction_id = data['data'].get('payment_transaction_id')
            p.transaction_ref_id = data['data'].get('transaction_ref_id')
            p.pg_transaction_id = data['data'].get('pg_transaction_id')
            p.status = data['data'].get('status')
            p.payment_gateway = data['data'].get('payment_gateway')
            p.amount = data['data'].get('amount')
            p.payment_mode = data['data'].get('payment_mode')
            p.payment_trial_no = data['data'].get('payment_trial_no')
            p.currency = data['data'].get('currency')
            p.fees = data['data'].get('fees')
            p.payment_time = data['data'].get('payment_time')
            p.whole_response = data['data'].get('whole_response')
            p.error_message = data['data'].get('error_message')
            # p.zapcash_ref = 
            p.save()

        return self.send_response(1, "Yeah mann!.You done it.")


