from django.shortcuts import render
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from zap_apps.zap_catalogue.helpers import checkAvailability, checkCartAvailibility, reduceCartQuantity, reduceQuantity, increaseCartQuantity
from zap_apps.order.models import Transaction as T, Order
from zap_apps.zap_catalogue.models import NumberOfProducts
from zap_apps.cart.models import Cart
import time, math
from zap_apps.logistics.models import DelhiveryPincode
from zap_apps.order.order_serializer import *
from zap_apps.payment.views import create_transaction
from zap_apps.payment.tasks import product_increase_quantity
import requests
import pdb
import json
# Create your views here.


def get_order_status(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return False
    # if order.returned:
    #     return "Returned"
    if hasattr(order,'returnmodel') and order.returnmodel.approved:
        return "Return approved"
    if hasattr(order,'returnmodel'):
        return "Return requested"
    if order.delivery_date:
        return "Delivered"
    else:
        return "Being Processed"

class Pincode(ZapView):
    def get(self, request, format=None):
        if request.GET.get('action') == 'cod':
            return self.send_response(1, DelhiveryPincode.objects.filter(pincode=request.GET.get('pincode'), cod='Y').exists())
        else:
            return self.send_response(1, DelhiveryPincode.objects.filter(pincode=request.GET.get('pincode')).exists())

class Transaction(ZapAuthView):

    def post(self, request, format=None):
        cart = Cart.objects.get(user=request.user, success=False)
        if checkCartAvailibility(cart.id):
            print '@@@@checkAvailability@@@'
            reduceCartQuantity(cart.id)

            # FIND TRANSACTION DATA FROM CART
            listing_price_sum = 0
            total_price = 0
            final_price = 0
            total_discount = 0
            listing_price_sum = cart.cart_price
            total_price = cart.cart_price_after_coupon
            final_price = total_price - request.data.get('zapcash', 0)
            # for item in cart.items.all():
            #     total_price += item.product.listing_price + (item.product.shipping_charge or 99)
            #     listing_price_sum += item.product.listing_price
            # if cart.coupon:
            #     if cart.coupon.abs_discount:
            #         total_discount = cart.coupon.abs_discount
            #     else:
            #         disc = (cart.coupon.perc_discount * total_price) / 100
            #         if cart.coupon.max_discount:
            #             if (disc < cart.coupon.max_discount):
            #                 total_discount = round((total_price - disc),0)
            #             else:
            #                 total_discount = round((total_price - max_discount),0)
            #         else:
            #             total_discount = round((total_price - disc),0)
            # final_price = total_price - total_discount - request.data.get('zapcash',0)
            cod = request.data.get('cod', 'false')
            # DO SAVE A TRANSACTION!

            print '200 ok 1'
            transaction_serializer = TransactionSerializer(data={
                'cart': cart.id, 'buyer': cart.user,
                'total_price': total_price,
                'final_price': final_price,
                'total_discount': total_discount,
                'listing_price_sum': listing_price_sum,
                'cod': cod,
                'offer': cart.offer if cart.offer else None,
                'transaction_ref': request.data['transaction_ref']})
            print '200 ok 2'
            if transaction_serializer.is_valid():
                print 'transaction_serializer is validddd'
                transaction = transaction_serializer.save()
                return self.send_response(1, {'transaction_id': transaction.id})
            print transaction_serializer.errors, ' invaid*******'
            return self.send_response(0, transaction_serializer.errors)
            # SCHEDULE A TASK TO INCREASE THE QUANTITY AFTER 10 MINS

        else:
            print '****sold out****'
            return self.send_response(0, 'Sorry! The product is sold out.')


class GetOrders(ZapAuthView):

    def get(self, request, format=None):
        print '>>>>>>>>>'
        orders = Order.objects.filter(transaction__buyer=request.user).order_by('id')
        srlzr = OrderSerializer(orders, many=True)
        # print srlzr.data,'---------'
        # print orders,'00000000'
        # print get_order_status(2)
        return self.send_response(1, srlzr.data)

class OrderDetails(ZapAuthView):

    def get(self, request, id, format=None):
        try:
            order = Order.objects.get(id=id)
        except:
            return self.send_response(0, 'Order not found.')
        srlzr = SingleOrderSerializer(order)
        return self.send_response(1, srlzr.data)

class OrderSummary(ZapAuthView):
    def get(self, request, order_id, format=None):
        # pdb.set_trace()
        try:
            trans = T.objects.get(buyer=request.user, transaction_ref=order_id)
            if trans.status in ['success','pending']:
                return render(request,'order/order.html',{'status':'success'})
            else:
                if int(trans.zapwallet_used):
                    wallet_amount = int(request.user.get_zap_wallet)
                    if trans.zapwallet_used > wallet_amount:
                            return render(request,'order/order.html', {'status':'error','detail':'You don"t have ZapCash to retry this payment.'})
                cart = request.user.cart
                if cart.is_empty():
                    return render(request,'order/order.html', {'status':'error','detail':"Items are not available in your cart."})
                if not checkCartAvailibility(cart.id):
                    return render(request,'order/order.html', {'status':'error','detail':"Products available is changed in cart."})
                cod = request.data.get('cod', False)
                if cod and cart.total_price_with_shipping_charge() > 90000:
                    return render(request,'order/order.html', {'status':'error','detail':"COD not available above Rs. 90000"})
                return render(request,'order/order.html',{
                    'status':'error',
                    'detail':'Something went wrong.',
                    'retry':True,
                    'address':cart.delivery_address_id,
                    'zapwallet_used':trans.zapwallet_used})
        except T.DoesNotExist:
            return render(request,'order/order.html',{'status':'error','detail':'Invalid order number.'})


class RateOrder(ZapAuthView):

    def post(self, request, format=None):
        data = request.data.copy()
        order_id = int(data['order_id'])
        rating = int(data['rating'])
        
        try:
            order = Order.objects.filter(pk=order_id)
            order = order[0]
            order.rating = rating
            order.save()

            print order.rating, "Order"

            data = [{'result': 'success'}]
            
        except Order.DoesNotExist:
            data = [{'result': 'success', 'message': 'No such order exists'}]
            return self.send_response(0, data)

        return self.send_response(1, data)

ORDER_TITLES = {
    'pending': 'Order is pending.',
    'failed': 'Order failed',
    'being_confirmed': 'Order being processed.',
    'cancelled': 'Order is cancelled.',
    'confirmed': 'Order is confirmed',
    'pickup_in_process': 'Order is getting picked up from Seller.',
    'picked_up': 'Order is picked up from Seller.',
    'verification': 'Checking Authenticity',
    'product_approved': 'Product Approved.',
    'product_rejected': 'Product Rejected',
    'on_the_way_to_you': 'On the way',
    'delivered': 'Delivered',
    'return_requested': 'Return Requested',
    'on_hold': 'Maximum delivery attempt exceeded',
    'return_in_process':'Return is in process',
    'returned':'Return Completed'
}
DEFAULT_RESPONSE = [
    {
        'status':'being_confirmed',
        'title':'Order being Confirmed',
        'description':'description'
    },
    {
        'status':'to_be_picked_up',
        'title':'Product is yet to be picked up from the Seller',
        'description':'description'
    },
    {
        'status':'to_be_verified',
        'title':'Zap Authentication yet to be done',
        'description':'description'
    },
    {
        'status':'to_be_shipped',
        'title':'Order yet to be Shipped',
        'description':'description'
    },
    {
        'status':'to_be_delivered',
        'title':'Order yet to be delivered.',
        'description':'description'
    }
]
import datetime
class TrackOrder(ZapView):
    

    def get(self,request, format=None):
        try:
            o = Order.objects.get(id=request.GET.get('order_id'))
            print o.order_status
            if o.order_status == 'being_confirmed':
                step = 0
                tracker = [DEFAULT_RESPONSE[0]]+[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif o.order_status == 'confirmed':
                step = 1
                tracker = [{'time':o.track_order.get(status='confirmed').time,'status':'confirmed'}]\
                +[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif o.order_status == 'pickup_in_process':
                step = 1
                tracker = [{'description':i.get_status_display(), 'title':ORDER_TITLES[i.status],'time':i.time} for i in o.track_order.filter(status__in=['confirmed'])]\
                +[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif o.order_status == 'picked_up':
                step = 2
                tracker = [{'description':i.get_status_display(), 'title':ORDER_TITLES[i.status],'time':i.time} for i in o.track_order.filter(status__in=['confirmed','picked_up'])]\
                +[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif o.order_status == 'verification':
                step = 2
                tracker = [{'description':i.get_status_display(), 'title':ORDER_TITLES[i.status],'time':i.time} for i in o.track_order.filter(status__in=['confirmed','picked_up','verification'])]\
                +[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]                
            elif o.order_status == 'product_approved':
                step = 3
                tracker = [{'description':i.get_status_display(), 'title':ORDER_TITLES[i.status],'time':i.time} for i in o.track_order.filter(status__in=['confirmed','picked_up','product_approved'])]\
                +[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif o.order_status == 'on_the_way_to_you':
                step = 4
                tracker = [{'description':i.get_status_display(), 'title':ORDER_TITLES[i.status],'time':i.time} for i in o.track_order.filter(status__in=['confirmed','picked_up','product_approved','on_the_way_to_you'])]\
                +[DEFAULT_RESPONSE[4]]
            elif o.order_status == 'delivered':
                step = 5
                tracker = [{'description':i.get_status_display(), 'title':ORDER_TITLES[i.status],'time':i.time} for i in o.track_order.filter(status__in=['confirmed','picked_up','product_approved','on_the_way_to_you','delivered'])]
            elif o.order_status == 'cancelled':
                tracker = o.track_order.filter(status__in=['confirmed','picked_up','product_approved','on_the_way_to_you','delivered']).values('time','status')
                +[{'status':'Order Cancelled','title':'Order has been Cancelled'}]

            else:
                tracker = [{}]
            return self.send_response(1, {'tracker':tracker,'current_step':step})
        except Exception as e:
            print e.message
            return self.send_response(0)    


import random
from zap_apps.payment.views import make_order, send_email_after_order_success
# import juspay as juspay
from zap_apps.payment.views import get_return_url
from django.conf import settings
from django.db.models import Sum, F

# class JuspayOrder(ZapView):
#     def __init__(self):
#         self.merchant_id = 'zapyle'
#         juspay.environment = settings.JUSPAY_ENV
#         juspay.api_key = settings.JUSPAY_API_KEY
#
#     def post(self, request, format=None):
#         # pdb.set_trace()
#
#         get_data = request.data.copy()
#         print get_data
#
#         user = request.user
#         cart = user.cart
#
#         if not get_data.get('order_id', False): #if not order update
#             if cart.is_empty():
#                 return self.send_response(0, "Please add items to your cart. Cart is empty now.")
#
#             if not checkCartAvailibility(cart.id):
#                 return self.send_response(0, "Product is Soldout.")
#
#             if not get_data.get('address_id'):
#                 return self.send_response(0, "Please select address.")
#
#         cod = get_data.get('cod', False)
#         emi = get_data.get('emi', False)
#
#         if cod and cart.total_price_with_shipping_charge() > 40000:
#             return self.send_response(0, "COD not available above Rs. 40000")
#
#         cart.delivery_address_id = get_data['address_id']
#         cart.save()
#         final_price = cart.total_price_with_shipping_charge()
#
#         apply_zapcash = get_data.get('apply_zapcash')
#
#         if apply_zapcash:
#             wallet_amount = 0
#             credit_return = user.zapcash_user1.filter(mode=2,credit=True).aggregate(s=Sum(F('amount')))['s'] or 0
#             debit_total = user.zapcash_user1.filter(credit=False).aggregate(s=Sum(F('amount')))['s'] or 0
#             promo_expense = credit_return - debit_total
#             max_promo = 0.2 * cart.total_listing_price()
#             promo_sum = user.zapcash_user1.filter(credit=True, mode__in=[0,1]).aggregate(s=Sum(F('amount')))['s'] or 0
#             if promo_expense > 0:
#                 wallet_amount = min(max_promo, promo_sum) + promo_expense
#             else:
#                 wallet_amount = min(max_promo, promo_sum+promo_expense)
#             wallet_amount
#             # wallet_amount = request.user.get_zap_wallet
#             sc = cart.total_shipping_charge()
#             lp = cart.total_listing_price()
#
#             if sc > 0 and wallet_amount > lp:
#                 wallet_amount = lp
#             zap_algo_return = self.zapcash_algo(
#                 wallet_amount, final_price)
#             final_price = zap_algo_return['total_amount']
#             wallet_to_use = zap_algo_return['zapwallet']
#         else:
#             wallet_to_use = 0
#
#         if cod:
#             return self.send_response(1, make_cod_transaction(cart, wallet_to_use, request))
#
#             # return self.send_response(1, get_data)
#
#         order_number = "OD" + "%.3f" % round(time.time(), 3)
#         order_number = order_number.replace('.', '')
#         if final_price > 0:
#             if get_data.get('order_id', False):
#                 try:
#                     trans = T.objects.get(transaction_ref=get_data.get('order_id'))
#                     trans.time = datetime.datetime.now()
#                     trans.save()
#                 except Exception as e:
#                     print e.message
#             else:
#                 data={
#                     'buyer': request.user,
#                     'transaction_ref': order_number,
#                     'zapwallet_used': wallet_to_use,
#                     'consignee': cart.delivery_address_id,
#                     'final_price': final_price,
#                     'offer': cart.offer.id if cart.offer else None,
#                     'payment_mode': 'juspay'
#                 }
#                 if emi:
#                     data['payment_mode'] = 'emi'
#                 data['platform'] = request.PLATFORM
#                 trans, valid = create_transaction(request.user, data)
#                 if not valid:
#                     return self.send_response(0, trans)
#                 if settings.CELERY_USE:
#                     for i in request.user.cart.item.all():
#                         zap_reduce_quantity(i.product.id, i.size.id, i.quantity)
#                     product_increase_quantity.apply_async((order_number,), countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)
#         else:
#             txn_id = str(int(time.time())) + str(random.randint(10000, 99999))
#             data={
#                 'status': 'success',
#                 'buyer': request.user,
#                 'transaction_ref': txn_id,
#                 'zapwallet_used': wallet_to_use,
#                 'payment_mode': 'wallet',
#                 'consignee': cart.delivery_address.id,
#                 'offer': cart.offer.id if cart.offer else None
#             }
#             data['platform'] = request.PLATFORM
#             transaction, valid = create_transaction(request.user, data)
#             if valid:
#                 make_order(transaction, cart)
#                 send_email_after_order_success(request, cart)
#                 return self.send_response(1, {'transaction_id': txn_id, 'message': 'TXSUCCESS'})
#             else:
#                 print transaction.errors, ' invaid*******'
#                 return self.send_response(0, 'Transactional error.')
#
#         user = request.user
#         if emi:
#             tenure = get_data.get('tenure')
#             interest = get_data.get('interest')
#             bank = get_data.get('bank')
#             monthly = round((final_price * ( (interest/1200.0) * pow( 1 + (interest/1200.0),tenure ) )/(pow(1+(interest/1200.0),tenure)-1)),2)
#             final_price = round(monthly * tenure * 100) / 100
#
#
#         # updating existing juspay order
#         if get_data.get('order_id', False):
#             my_new_order = juspay.Orders.update(order_id=get_data.get('order_id'), amount=final_price)
#             order_number = get_data.get('order_id')
#         else:
#             my_new_order = juspay.Orders.create(
#                 order_id=order_number,
#                 amount=final_price,
#                 return_url = settings.DOMAIN_NAME + '/payment/zappaymentreturn/juspay/website/',
#                 customer_id = user.id,
#                 customer_email = user.email,
#                 customer_phone =  user.phone_number,
#                 description = 'empty'
#             )
#         print my_new_order,'my_new_order', user.phone_number, 'phon'
#         response_data = {
#                 'iframe':my_new_order.payment_links.iframe,
#                 'id':my_new_order.id,
#                 'mobile_url':my_new_order.payment_links.mobile,
#                 'order_id':order_number,
#                 'message': 'TXFWD',
#                 'amount_pay':final_price,
#                 'endURL':settings.DOMAIN_NAME + '/payment/zappaymentreturn/juspay/website/',
#                 'timeout_min' : 10
#             }
#         if emi:
#             response_data['emi_iframe'] = "https://api.juspay.in/merchant/ipay?merchant_id={}&order_id={}&is_emi=true&emi_tenure={}&emi_bank={}".format(self.merchant_id,order_number,tenure,bank)
#             response_data['monthly_amount'] = monthly
#         return self.send_response(1, response_data)
#
#     def zapcash_algo(self, zapwallet, total_amount):
#         if zapwallet >= total_amount:
#             zapwallet_used = total_amount
#             total_amount = 0
#         else:
#             total_amount -= zapwallet
#             zapwallet_used = zapwallet
#         return {
#             'zapwallet': zapwallet_used,
#             'total_amount': total_amount
#             }
#
#     def put(self, request, format=None):
#         transaction = T.objects.get(transaction_ref=request.data['order_id'])
#         if settings.CELERY_USE:
#             product_increase_quantity(transaction.transaction_ref)
#         transaction.status = 'cancelled'
#         transaction.save()
#         return self.send_response(1, 'success')


def make_cod_transaction(cart, zapwallet, request=None):

    order_number = "OD" + "%.3f" % round(time.time(), 3)
    order_number = order_number.replace('.', '')
    final_price = cart.total_price_with_shipping_charge() - zapwallet
    data={
        'status': 'success',
        'buyer': cart.user,
        'transaction_ref': order_number,
        'zapwallet_used': zapwallet,
        'payment_mode': 'cod',
        'consignee': cart.delivery_address.id,
        'final_price': final_price,
        'offer': cart.offer.id if cart.offer else None
    }
    data['platform'] = request.PLATFORM
    transaction, valid = create_transaction(cart.user, data)
    if valid:
        make_order(transaction, cart)
        send_email_after_order_success(request, cart)
        return {
            'transaction_id': order_number, 
            'message': 'TXSUCCESS', 
            'order_id': order_number, 
            'amount_pay':final_price, 
            'detail':'Your order has been placed successfully Please pay the delivery person an amount of '+str(final_price)
            }
    else:
        return {}

def zap_reduce_quantity(p, s, q):
    num_of_p = NumberOfProducts.objects.get(
            product=p, size=s)
    if num_of_p.quantity - q <= 0:
        num_of_p.quantity = 0
    else:
        num_of_p.quantity = num_of_p.quantity - q
    num_of_p.save()


def monthly_amount(tenure, interest, amount):
    monthly_interest = interest/1200.0
    monthlyamount = amount * (monthly_interest * pow(1 + monthly_interest, int(tenure))) / (pow(1 + monthly_interest, int(tenure)) - 1)
    monthlyamount = round(monthlyamount, 2)
    return monthlyamount


class EMI_Payment(ZapView):
    def get(self, request, format=None):

        amount = int(request.GET.get('amount','0'))
        url = "https://api.razorpay.com/v1/methods?key_id=rzp_live_FoWFOe8bVF8C4s"
        response = requests.get(url=url).json()

        if response.has_key("error"):
            return self.send_response(0, response['error']['description'])
        banks = {}
        for i in response["emi_plans"].iteritems():
            if i[1]["min_amount"] <= amount*100:
                bank_plans = {}
                for key in i[1]["plans"].keys():
                    monthlyamount = monthly_amount(key, i[1]["plans"][key], amount)
                    bank_plans.update({key: (i[1]["plans"][key], monthlyamount, round(monthlyamount*int(key), 2))})
                banks.update({i[0]:bank_plans})
        # banks = {i[0]: (i[1]["plans"], monthly_amount(i[0], i[1]["plans"], amount), monthly_amount(i[0], i[1]["plans"], amount) * i[0]) for i in response["emi_plans"].iteritems() if i[1]["min_amount"]<=amount*100}
        return self.send_response(1, banks)

