from __future__ import division
import json
import hmac
import time
import random
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Sum, F
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from hashlib import sha1, sha256
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from zap_apps.payment.models import BillGeneratorModel, PaymentResponse
from zap_apps.payment.payment_serializer import TransSrlzr, BillGeneratorSrlzr, BillGeneratorModelSrlzr, PaymentResponseSerializer, GetTransactionSerializer, SingleTransactionSerializer, RefundResponseSerializer
from zap_apps.zap_catalogue.models import ApprovedProduct, NumberOfProducts
from zap_apps.address.models import Address
from zap_apps.order.models import Transaction, OrderedProduct, OrderTracker
from zap_apps.order.order_serializer import OrderSerializer, TransactionSerializer
from zap_apps.zap_catalogue.helpers import increaseCartQuantity
from zap_apps.cart.models import Cart
from zap_apps.zap_notification.tasks import zaplogging
from zap_apps.zap_notification.views import ZapSms, ZapEmail
from zap_apps.zap_catalogue.helpers import checkCartAvailibility
from zap_apps.order.tasks import seller_address_conf_after_order
from zap_apps.extra_modules.appvirality import AppViralityApi
from zap_apps.zapuser.models import AppViralityKey
from zap_apps.extra_modules.tasks import app_virality_conversion
import pdb
from httplib2 import Http
from urllib import urlencode
import requests
from zap_apps.zap_catalogue.product_serializer import ProductImageSerializer
from django.http import JsonResponse
from zap_apps.cart.cart_serializers import CartSerializerForTransaction
from zap_apps.payment.tasks import check_pending_transaction
from zap_apps.payment.tasks import product_increase_quantity


def zap_reduce_quantity(p, s, q):
    num_of_p = NumberOfProducts.objects.get(
            product=p, size=s)
    if num_of_p.quantity - q <= 0:
        num_of_p.quantity = 0
    else:
        num_of_p.quantity = num_of_p.quantity - q
    num_of_p.save()

def zap_increase_quantity(p, s, q):
    num_of_p = NumberOfProducts.objects.get(
            product=p, size=s)
    num_of_p.quantity = num_of_p.quantity + q
    num_of_p.save()
class AccessKeyVanity(ZapAuthView):

    def get(self, request, format=None):
        return self.send_response(
            1,
            {'access_key': settings.MERCHANT_ACCESS_KEY,
                'vanity_url': settings.MERCHANT_VANITY_URL,
                'citrus_env': settings.CITRUS_ENV}
        )

    def add_zapcash_entry(self, d):
        ZapCash.objects.create(**d)
def make_orderered_product(item):
    product = item.product
    try:
        with open(product.images.all().order_by('id')[0].image.path, "rb") as f:
            data = f.read()
            data = data.encode("base64")
        img_serializer = ProductImageSerializer(
                    data={'image': data})
        img_serializer.is_valid()
        img_serializer.save()
    except Exception:
        pass
     #
    op = OrderedProduct()
    try:
        op.image_id = img_serializer.data['id']
    except Exception:
        op.image_id = None
    op.title = product.title
    op.description = product.description
    op.style = product.style.style_type if product.style else "no style"
    op.brand = product.brand.brand
    op.original_price = product.original_price
    op.listing_price = product.listing_price
    op.size = item.get_size_string()
    op.occasion = product.occasion.name if product.occasion else "no occasion"
    op.product_category = product.product_category.name
    op.color = product.color.name if product.color else "no color"
    op.age = product.get_age_display()
    op.condition = product.get_condition_display()
    op.percentage_commission = product.percentage_commission
    op.with_zapyle = product.with_zapyle
    op.save()
    return op
def success_order_follow_up(transaction):
    if transaction.zapwallet_used:
        transaction.buyer.redeem_zap_wallet(transaction.zapwallet_used, transaction)
    if settings.APPVIRALITY_ENABLE:
        if settings.CELERY_USE:
            app_virality_conversion.delay(transaction.buyer.id, "BuyOrSell", "Buy")
        else:
            app_virality_conversion(transaction.buyer.id, "BuyOrSell", "Buy")
    for order in transaction.order.all():
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if settings.CELERY_USE:
                seller_address_conf_after_order.delay(order.id)
            else:
                seller_address_conf_after_order(order.id)

def make_order(transaction, cart):
    for item in cart.item.all():
        order_number = "OD" + "%.3f" % round(time.time(), 3)
        order_number = order_number.replace('.', '')
        op = make_orderered_product(item)

        # print (item.price()/cart.total_price_with_shipping_charge())*transaction.zapwallet_used
        # print item.price(), cart.total_price_with_shipping_charge(), transaction.zapwallet_used
        data={
            'shipping_charge': settings.SHIPPING_CHARGE if item.selling_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0,
            'product': item.product.id,
            'transaction': transaction.id,
            'order_number': order_number,
            'ordered_product': op.id,
            'quantity': item.quantity,
            'consignor': item.product.pickup_address.id,
            'final_price': item.selling_price,
            'zapwallet_used': (item.price()/cart.total_price_with_shipping_charge())*transaction.zapwallet_used
        }
        if item.offer:
            data['offer'] = item.offer.id 
        if transaction.status == 'pending':
            data['order_status'] = 'pending'
        if item.product.with_zapyle:
            data['confirmed_with_seller'] = True
        serializer = OrderSerializer(data=data)
        if not serializer.is_valid():
            print serializer.errors
            return None
        srlzr = serializer.save()
        no_of_prod = item.product.product_count.get(size=item.size)
        no_of_prod.quantity -= item.quantity
        no_of_prod.save()
        OrderTracker.objects.create(orders_id=srlzr.id,status="being_confirmed")
    if not transaction.status == 'pending':
        success_order_follow_up(transaction)



def save_payment_response(transaction,data,status):
    payment_serializer = PaymentResponseSerializer(
        data={
            'transaction': transaction.id,
            'payment_success': status,
            'payment_id': data.get('transactionId'),
            'payment_transaction_id': data['TxId'],
            'pg_transaction_id': data['pgTxnNo'],
            'marketplaceTxId': data.get('marketplaceTxId',''),
            'transaction_ref_id': data['TxRefNo'],
            'status': data['TxStatus'],
            'payment_gateway': data['TxGateway'],
            'amount': data['amount'],
            'payment_mode': data['paymentMode'],
            'currency': data['currency'],
            'payment_time': data['txnDateTime'],
            'whole_response': dict(data),
            'issuer_ref_no': data['issuerRefNo'],
            'auth_id_code': data['authIdCode'],
            'currency': data['currency'],
            'merchant_transaction_id': data['TxId']})

    if payment_serializer.is_valid():
        paymentlog = payment_serializer.save()
    return True
def get_image_domain(request):
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = get_current_site(request)
    return "{0}://{1}".format(
        protocol,
        current_site.domain
    )
def send_email_after_order_success(request, cart, wallet=0):
    zapemail = ZapEmail()
    items = cart.item.all()
    html = settings.ORDER_COFIRMED_HTML_1
    current_user = cart.user
    image_domain = get_image_domain(request)
    full_price = cart.total_price_with_shipping_charge()
    email_vars = {
        'buyer_name': current_user.get_full_name() or current_user.zap_username,
        'shipping_charge': cart.total_shipping_charge(),
        'final_price': str(full_price),
        'items':[{
        'productImage': image_domain + item.product.images.all()[0].image.url_100x100,
        'product_title': item.product.title,
        'product_qty': item.quantity,
        'zapwallet_used': (item.price()/cart.total_price_with_shipping_charge())*wallet,
        'unit_price': item.selling_price
        } for item in items]
    }
    print email_vars
    html_body = render_to_string(
        html['html'],email_vars)

    zapemail.send_email_alternative(html[
                        'subject'], settings.FROM_EMAIL, current_user.email, html_body)

    # zapemail.send_email(html['html'], html[
    #                     'subject'], email_vars, settings.FROM_EMAIL, current_user.email)
    html = settings.ORDER_COFIRMED_HTML_2
    email_vars = {
        'order_items': [{
            'buyer': current_user.get_full_name() or current_user.zap_username,
            'seller': item.product.user.get_full_name() or item.product.user.zap_username,
            'album_name': item.product.title,
            'productImage': image_domain + item.product.images.all()[0].image.url_100x100,
            'listing_price': item.selling_price,
            'quantity': item.quantity
        } for item in items]
    }

    html_body = render_to_string(
    html['html'], email_vars)

    zapemail.send_email_alternative(html[
                        'subject'], settings.FROM_EMAIL, "zapyle@googlegroups.com", html_body)

    if not settings.CELERY_USE:
        for i in cart.item.all():
            zap_reduce_quantity(i.product.id, i.size.id, i.quantity)
    cart.item.all().delete()
    cart.offer = None
    cart.save()

    # zapemail.send_email(html['html'], html[
    #                     'subject'], email_vars, settings.FROM_EMAIL, "zapyle@googlegroups.com")
    
    # html = settings.ORDER_COFIRMED_SELLER_HTML
    # pickup_address = item.product.pickup_address
    # full_address = pickup_address.name +", "+ pickup_address.address+", "+ (pickup_address.address2 + "," if pickup_address.address2 else "")+pickup_address.city+", "+pickup_address.state.name+", "+pickup_address.pincode+"."
    # email_vars = {
    #     'user': item.product.user.get_full_name() or transaction.cart.items.all()[0].product.user.zap_username,
    #     'product_title': item.product.title,
    #     'product_pickup_address': full_address
    # }

    # zapemail.send_email(html['html'], html[
    #                     'subject'], email_vars, settings.FROM_EMAIL, item.product.user.email)
    return True


def send_email_after_delayed_order_success(transaction):
    # pdb.set_trace()
    zapemail = ZapEmail()
    html = settings.ORDER_COFIRMED_HTML_1
    current_user = transaction.buyer
    image_domain = settings.CURRENT_DOMAIN
    all_orders = transaction.order.all()
    full_price = transaction.total_price_with_shipping_charge()
    email_vars = {
        'buyer_name': current_user.get_full_name() or current_user.zap_username,
        'shipping_charge': transaction.shipping_charge(),
        'final_price': str(full_price),
        'items':[{
        'productImage': image_domain + order.ordered_product.image.image.url_100x100,
        'product_title': order.ordered_product.title,
        'product_qty': order.quantity,
        'zapwallet_used': order.zapwallet_used,
        'unit_price': order.final_price,
        } for order in all_orders]
    }
    html_body = render_to_string(
        html['html'],email_vars)

    zapemail.send_email_alternative(html[
                        'subject'], settings.FROM_EMAIL, current_user.email, html_body)
    html = settings.ORDER_COFIRMED_HTML_2
    email_vars = {
        'order_items': [{
            'buyer': current_user.get_full_name() or current_user.zap_username,
            'seller': order.product.user.get_full_name() or order.product.user.zap_username,
            'album_name': order.ordered_product.title
        } for order in all_orders]
    }

    html_body = render_to_string(
    html['html'], email_vars)

    zapemail.send_email_alternative(html[
                        'subject'], settings.FROM_EMAIL, "zapyle@googlegroups.com", html_body)
    all_orders.update(order_status='being_confirmed')



def generateSignature(final_price, txn_id=None):
    access_key = settings.MERCHANT_ACCESS_KEY
    secret_key = settings.MERCHANT_SECRET_KEY
    if not txn_id:
        txn_id = str(int(time.time())) + str(random.randint(10000, 99999))
    # data_string = "merchantAccessKey=" + access_key + \
    #     "&transactionId=" + txn_id + "&amount=" + str(int(final_price))
    data = 'merchantAccessKey=' + access_key + '&transactionId=' + txn_id + '&amount=' + str(final_price)
    hm = hmac.new(secret_key, data, sha1)
    signature = hm.hexdigest()
    return signature

def citrus_refund(data):
    url = settings.CITRUS_REFUND_URL
    try:
        print 'test1'
        # h = Http()
        print 'test2'
        msg = "refund-citrus-data-{}".format(json.dumps(data))
        zaplogging.delay(msg) if settings.CELERY_USE else zaplogging(msg)

        signature = generateSignature(data['amount'],data['merchantTxnId'])
        headers = {u'Content-Type': 'application/json', 'signature': signature, 'access_key':settings.MERCHANT_ACCESS_KEY, 'Accept':'application/json'}
        resp = requests.post(url, json.dumps(data), headers=headers)

        msg = "refund-response-{}".format(resp)
        zaplogging.delay(msg) if settings.CELERY_USE else zaplogging(msg)
        if resp.status_code == 200:
            json_response = resp.json()
            return json_response
        return False
        #
        # # data needs to be written somewhere
        # # if 'success' in packaging_json_response and
        # # packaging_json_response['success'] is True:
        # return json_response
        # return None
    except:
        return False
class Refund(ZapView):
    def post(self, request, format=None):

        from zap_apps.payment.models import ZapWallet
        from zap_apps.order.models import Order
        from zap_apps.logistics.tasks import decryptAcc

        zapemail = ZapEmail()
        data = request.data.copy()
        refund_mode = data['refund_mode']
        order = Order.objects.get(id=data['order_id'])
        returns = order.returnmodel
        buyer = order.transaction.buyer
        credited = ''
        if refund_mode == 'account_transfer' and order.final_payable_price:
            if order.transaction.payment_mode == 'cod':
                userdata = buyer.user_data
                if userdata.account_number and userdata.account_holder and userdata.ifsc_code:
                    email_body = "Greetings,\n\nPlease make a payment for returns to the below given buyer.\n\nAccount Holder Name: "+userdata.account_holder+"\nAccount Number: "+decryptAcc(userdata.account_number)+"\nIFSC No.: "+userdata.ifsc_code+"\nAmount: "+str(order.final_payable_price)
                    zapemail.send_email_attachment(Refund+" Order - : "+order.order_number,settings.FROM_EMAIL,['shafi@zapyle.com'],email_body=email_body) #,'accounts@zapyle.com', 'likhita@zapyle.com'
                    credited = 'initiated'
                    refund_srlzr_data = {'order':order.id, 'amount':str(order.final_payable_price), 'mode':'manual', 'whole_response':"Email Sent to accounts for refund. You should make it to completed once done."}
                    srlzr = RefundResponseSerializer(data=refund_srlzr_data)
                    if srlzr.is_valid():
                        srlzr.save()
                    credited = 'refunded'
                #send email to accounts
                else:
                    print 'Not Successfull'
                    #send them email
            else:
                payment_resp = order.transaction.payment_response.filter(payment_success=True)[0]
                currency = payment_resp.currency or 'INR'
                refund_data = {"merchantTxnId": payment_resp.merchant_transaction_id, "pgTxnId": payment_resp.pg_transaction_id,
                    "rrn":payment_resp.issuer_ref_no, "authIdCode":payment_resp.auth_id_code, "currencyCode": currency,
                    "amount":order.final_payable_price(), "txnType":'Refund'}
                acc_refund = citrus_refund(refund_data)
                pdb.set_trace()
                if acc_refund:
                    refund_srlzr_data = {'order':order.id, 'amount':acc_refund['amount'], 'mode':'citrus', 'whole_response':json.dumps(acc_refund)}
                    srlzr = RefundResponseSerializer(data=refund_srlzr_data)
                    if srlzr.is_valid():
                        srlzr.save()
                    credited = 'refunded'
        else:
            if order.final_payable_price:
                buyer.issue_zap_wallet(order.final_payable_price, mode='2', purpose='Issued for return against actual cash', return_id=returns)
            credited = 'refunded'
        if order.zapwallet_used:

            # buyer.issue_zap_wallet(order.zapwallet_used, mode='1', purpose='ZapWallet issued for return')
            fraction = order.total_price()/ (order.transaction.listing_price() + order.transaction.shipping_charge())
            debit_wallets = order.transaction.transaction_id1.filter(credit=False)
            for wallet in debit_wallets:
                buyer.issue_zap_wallet((fraction*order.zapwallet_used), mode=wallet.mode, purpose='ZapWallet issued for return', return_id=returns)
        returns.refund_mode = refund_mode
        returns.save()
        order.refund_status = credited
        order.save()
        return self.send_response(1, "Refund Initiated")

class WebsiteNotifyUrl(ZapView):
    def post(self, request, format=None):
        zaplogging.delay("notify"+str(request.data.copy())) if settings.CELERY_USE else zaplogging("notify"+str(request.data.copy()))
        return self.send_response(0, "Yeah done!")


class WebsiteReturnUrl(ZapView):

    def post(self, request, format=None):
        data = request.data.copy()
        zaplogging.delay("website" + str(data)) if settings.CELERY_USE else zaplogging("website" + str(data))
        print data, ' WebsiteReturnUrl'
        secret_key = settings.MERCHANT_SECRET_KEY
        data_string = data['TxId'] + data['TxStatus'] + data['amount'] + data['pgTxnNo'] + data['issuerRefNo'] + \
            data['authIdCode'] + data['firstName'] + data[
                'lastName'] + request.data['pgRespCode'] + request.data['addressZip']
        hm = hmac.new(secret_key, data_string, sha1)
        signature = hm.hexdigest()
        transaction = Transaction.objects.get(
            transaction_ref=request.data['TxId'])
        transaction.payment_mode = 'debit_card' if data['paymentMode'] == 'DEBIT_CARD' else \
        'credit_card' if data['paymentMode'] == 'CREDIT_CARD' else 'netbanking'
        print signature,">>>",data['signature']
        if signature == data["signature"]:
            if "SUCCESS" in data['TxStatus'].upper():
                transaction.status = 'success'
                transaction.save()
                make_order(transaction, transaction.buyer.cart)
                save_payment_response(transaction, data, True)
                send_email_after_order_success(request, transaction.buyer.cart, transaction.zapwallet_used)
            elif "FORWARD" in data['TxStatus'].upper():
                transaction.status = 'pending'
                transaction.save()
                make_order(transaction, transaction.buyer.cart)
                save_payment_response(transaction, data, False)
                if settings.CELERY_USE:
                    check_pending_transaction.apply_async(args=[transaction.id], countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)
                else:
                    check_pending_transaction(transaction.id)
            else:
                if settings.CELERY_USE:
                    product_increase_quantity(transaction.transaction_ref)
                transaction.status = 'failed'
                transaction.save()
                save_payment_response(transaction, data, False)
                context = {'data': dict(request.data)}
                print "Transaction Failed"
        else:
            if settings.CELERY_USE:
                product_increase_quantity(transaction.transaction_ref)
            transaction.status = 'sig_mismatch'
            transaction.save()
            save_payment_response(transaction, data, False)
            context = {'data': dict(request.data)}
            context = {'data': "error"}
            print "signature didn't match"
        # request.user.profile.profile_completed = 5
        # request.user.profile.save()
        r_url = "/order/" + str(data['TxId'])
        return HttpResponseRedirect(r_url)



class ReturnUrl(ZapView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'returnbill.html'

    def post(self, request, format=None):
        secret_key = settings.MERCHANT_SECRET_KEY
        data = request.data.copy()
        zaplogging.delay("app" + str(data)) if settings.CELERY_USE else zaplogging("app" + str(data))
        data_string = data['TxId'] + data['TxStatus'] + data['amount'] + data['pgTxnNo'] + data['issuerRefNo'] + \
            data['authIdCode'] + data['firstName'] + data['lastName'] + data['pgRespCode'] + data['addressZip']
        hm = hmac.new(secret_key, data_string, sha1)
        signature = hm.hexdigest()
        transaction = Transaction.objects.get(
            transaction_ref=request.data['TxId'])
        transaction.payment_mode = 'debit_card' if data['paymentMode'] == 'DEBIT_CARD' else \
        'credit_card' if data['paymentMode'] == 'CREDIT_CARD' else 'NETBANKING'
        print signature,">>>",data['signature']
        if signature == data["signature"]:
            if "SUCCESS" in request.data['TxStatus'].upper():
                transaction.status = 'success'
                transaction.save()
                make_order(transaction, transaction.buyer.cart)
                save_payment_response(transaction, data,True)
                send_email_after_order_success(request, transaction.buyer.cart)
            elif "FORWARD" in data['TxStatus'].upper():
                transaction.status = 'pending'
                transaction.save()
                make_order(transaction, transaction.buyer.cart)
                save_payment_response(transaction, data, False)
                if settings.CELERY_USE:
                    check_pending_transaction.apply_async(args=[transaction.id], countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)
                else:
                    check_pending_transaction(transaction.id)
            else:
                if settings.CELERY_USE:
                    product_increase_quantity(transaction.transaction_ref)
                transaction.status = 'failed'
                transaction.save()
                save_payment_response(transaction,request.data,False)
        else:
            if settings.CELERY_USE:
                product_increase_quantity(transaction.transaction_ref)
            transaction.status = 'sig_mismatch'
            transaction.save()
            save_payment_response(transaction, data, False)
        try:
            tx_id = data.get('TxId')
            tx_status = data.get('TxStatus')
            amount = data.get('amount')
            pg_txn_no = data.get('pgTxnNo')
            issuer_ref_no = data.get('issuerRefNo')
            auth_id_code = data.get('authIdCode')
            first_name = data.get('firstName')
            last_name = data.get('lastName')
            pg_resp_code = data.get('pgRespCode')
            address_zip = data.get('addressZip')
            payment_message = data.get('TxMsg', None)
            payment_status = data.get('TxStatus', None)
            payment_mode = data.get('paymentMode', None)
            payment_gateway = data.get('TxGateway', None)
            data_string = str(tx_id) + str(tx_status) + str(amount) + str(pg_txn_no) + str(issuer_ref_no) + \
                str(auth_id_code) + str(first_name) + \
                str(last_name) + str(pg_resp_code)
            if address_zip:
                data_string += str(address_zip)
            context = {'data': json.dumps(data)}
            return Response(context)
        except Exception as e:
            print e, 'Exception'
            context = {'data': 'error'}
            return Response(context)


def get_return_url(request, action_from):
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = get_current_site(request)
    return "{0}://{1}{2}".format(
        protocol,
        current_site.domain,
        ("/payment/zappaymentreturn/website/" if not action_from=='android' else "/payment/zappaymentreturn/")
    )
def get_notify_url(request, action_from):
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = get_current_site(request)
    return "{0}://{1}{2}".format(
        protocol,
        current_site.domain,
        ("/payment/notify/website/" if not action_from=='android' else "/payment/notify/")
    )

def zap_bill_generator(request, final_price, txn_id=None,action_from='android'):
    access_key = settings.MERCHANT_ACCESS_KEY
    secret_key = settings.MERCHANT_SECRET_KEY
    if not txn_id:
        txn_id = str(int(time.time())) + str(random.randint(10000, 99999))
    data_string = "merchantAccessKey=" + access_key + \
        "&transactionId=" + txn_id + "&amount=" + str(int(final_price))
    hm = hmac.new(secret_key, data_string, sha1)
    signature = hm.hexdigest()
    amount = {"value": str(int(final_price)), "currency": "INR"}
    return {
        "merchantTxnId": txn_id,
        "amount": amount,
        "requestSignature": signature,
        "merchantAccessKey": access_key,
        "returnUrl": get_return_url(request, action_from),
        "notifyUrl": get_return_url(request, action_from)
    }

def create_transaction(user, data):
    # Transaction.objects.filter(buyer=user, status__isnull=True).update()
    # try:
    #     trans =
    # except Transaction.MultipleObjectsReturned:
    #     try:
    #         Transaction.objects.filter(buyer=user, status__isnull=True).update(deleted=True)
    #         raise Transaction.DoesNotExist
    #     except Transaction.DoesNotExist:
    #         trans = Transaction.objects.create(buyer=user)
    # except Transaction.DoesNotExist:
    trans = Transaction.objects.create(buyer=user)
    transaction_serializer = TransactionSerializer(trans, data=data,partial=True)
    return_value = transaction_serializer.is_valid()
    if return_value:
        trans = transaction_serializer.save()
    else:
        trans = transaction_serializer.errors
    return trans, return_value

class WebsiteBillGenerator(ZapAuthView):

    def zapcash_algo(self, zapwallet, total_amount):
        if zapwallet >= total_amount:
            zapwallet_used = total_amount
            total_amount = 0
        else:
            total_amount -= zapwallet
            zapwallet_used = zapwallet
        return {'zapwallet': zapwallet_used, 'total_amount': total_amount}

    def post(self, request, format=None):
        cart = request.user.cart
        if cart.is_empty():
            return self.send_response(0, "Please add items to your cart. Cart is empty now.")
        if not checkCartAvailibility(cart.id):
            return self.send_response(0, "Product is Soldout.")
        data = request.data.copy()
        if not data.get('address_id'):
            return self.send_response(0, "Please select address.")
        cod = data.get('cod')
        if cod and cart.total_price_with_shipping_charge() > 30000:
            return self.send_response(0, "COD not available above Rs. 30000")
        cart.delivery_address_id = data['address_id']
        cart.save()
        final_price = cart.total_price_with_shipping_charge()

        apply_zapcash = data.get('apply_zapcash')
        if apply_zapcash:
            wallet_amount = request.user.get_zap_wallet
            sc = cart.total_shipping_charge()
            lp = cart.total_listing_price()
            if sc > 0 and wallet_amount > lp:
                wallet_amount = lp
            zap_algo_return = self.zapcash_algo(
                wallet_amount, final_price)
            final_price = zap_algo_return['total_amount']
            wallet_to_use = zap_algo_return['zapwallet']
        else:
            wallet_to_use = 0
        if cod:
            return self.send_response(1, make_cod_transaction(cart, wallet_to_use, request))
        if final_price > 0:
            bill = zap_bill_generator(request, final_price, action_from='website')
            zaplogging.delay("website"+str(bill)) if settings.CELERY_USE else zaplogging("website"+str(bill))
            bill['message'] = 'TXFWD'
            data={
                'buyer': request.user,
                'transaction_ref': bill['merchantTxnId'],
                'zapwallet_used': wallet_to_use,
                'consignee': cart.delivery_address.id,
                'final_price': final_price
            }
            data['platform'] = 'WEBSITE'
            trans, valid = create_transaction(request.user, data)
            if not valid:
                return self.send_response(0, trans)
            if settings.CELERY_USE:
                for i in request.user.cart.item.all():
                    zap_reduce_quantity(i.product.id, i.size.id, i.quantity)
                product_increase_quantity.apply_async((bill['merchantTxnId'],), countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)
            return self.send_response(1, bill)
        else:
            txn_id = str(int(time.time())) + str(random.randint(10000, 99999))
            data={
                'status': 'success',
                'buyer': request.user,
                'transaction_ref': txn_id,
                'zapwallet_used': wallet_to_use,
                'payment_mode': 'wallet',
                'consignee': cart.delivery_address.id
            }
            data['platform'] = 'WEBSITE'
            transaction, valid = create_transaction(request.user, data)
            if valid:
                make_order(transaction, cart)
                send_email_after_order_success(request, cart)
                return self.send_response(1, {'transaction_id': txn_id, 'message': 'TXSUCCESS'})
            else:
                print transaction.errors, ' invaid*******'
                return self.send_response(0, 'Transactional error.')
    def put(self, request, format=None):
        transaction = Transaction.objects.get(transaction_ref=request.data['TxId'])
        if settings.CELERY_USE:
            product_increase_quantity(transaction.transaction_ref)
        transaction.status = 'sig_mismatch'
        transaction.save()        
        return self.send_response(1, 'success')


def make_cod_transaction(cart, zapwallet, request=None):

    txn_id = str(int(time.time())) + str(random.randint(10000, 99999))
    data={
        'status': 'success',
        'buyer': cart.user,
        'transaction_ref': txn_id,
        'zapwallet_used': zapwallet,
        'payment_mode': 'cod',
        'consignee': cart.delivery_address.id,
        'final_price': cart.total_price_with_shipping_charge() - zapwallet
    }
    if request.PLATFORM in ['IOS','ANDROID']:
        data['platform'] = request.PLATFORM
    else:
        data['platform'] = 'WEBSITE'


    transaction, valid = create_transaction(cart.user, data)
    if valid:
        make_order(transaction, cart)
        send_email_after_order_success(request, cart)
        return {'transaction_id': txn_id, 'message': 'TXSUCCESS'}
    else:
        return {}


class BillGenerator(ZapView):

    def zapcash_algo(self, zapwallet, total_amount):
        if zapwallet >= total_amount:
            zapwallet_used = total_amount
            total_amount = 0
        else:
            total_amount -= zapwallet
            zapwallet_used = zapwallet
        return {'zapwallet': zapwallet_used, 'total_amount': total_amount}

    @method_decorator(zap_login_required)
    def post(self, request, t_ref=None, format=None):
        print request.data
        cart = request.user.cart
        if cart.is_empty():
            return self.send_response(0, "Please add items to your cart. Cart is empty now.")
        if not checkCartAvailibility(cart.id):
            return self.send_response(0, "Products available is changed in cart.")
        data = request.data.copy()
        if not data.get('address_id'):
            return self.send_response(0, "Please select address.")
        cod = data.get('cod')
        if cod and cart.total_price_with_shipping_charge() > 90000:
            return self.send_response(0, "COD not available above Rs. 90000")
        cart.delivery_address_id = data['address_id']
        cart.save()
        final_price = cart.total_price_with_shipping_charge()

        apply_zapcash = data.get('apply_zapcash')
        if apply_zapcash:
            wallet_amount = request.user.get_zap_wallet
            sc = cart.total_shipping_charge()
            lp = cart.total_listing_price()
            if sc > 0 and wallet_amount > lp:
                wallet_amount = lp
            zap_algo_return = self.zapcash_algo(
                wallet_amount, final_price)
            final_price = zap_algo_return['total_amount']
            wallet_to_use = zap_algo_return['zapwallet']
        else:
            wallet_to_use = 0
        if cod:

            return self.send_response(1, make_cod_transaction(cart, wallet_to_use, request))
        if final_price > 0:
            bill = zap_bill_generator(request, final_price,action_from='android')
            data={
                'buyer': request.user,
                'transaction_ref': bill['merchantTxnId'],
                'zapwallet_used': wallet_to_use,
                'consignee': cart.delivery_address.id,
                'final_price': final_price
            }
            data['platform'] = request.PLATFORM
            transaction, valid = create_transaction(request.user, data)
            if not valid:
                return self.send_response(0, transaction)
            zaplogging.delay("android"+str(bill)) if settings.CELERY_USE else zaplogging("android"+str(bill))
            bill = {'message': 'TXFWD',
                    'amount_pay': final_price,
                    'transaction_ref': bill['merchantTxnId']
                    }
            return self.send_response(1, bill)

        else:
            txn_id = str(int(time.time())) + str(random.randint(10000, 99999))
            data={
                'status': 'success',
                'buyer': request.user,
                'transaction_ref': txn_id,
                'zapwallet_used': wallet_to_use,
                'payment_mode': 'wallet',
                'consignee': cart.delivery_address.id
            }
            data['platform'] = request.PLATFORM
            transaction, valid = create_transaction(request.user, data)
            if valid:
                make_order(transaction, cart)
                send_email_after_order_success(request, cart)
                return self.send_response(1,{'transaction_id': txn_id,'message':'TXSUCCESS'})
            else:
                return self.send_response(0, "Transactional error.")

    def get(self, request, t_ref=None, apply_zapcash=None, format=None):
        try:
            transaction = Transaction.objects.get(transaction_ref=t_ref)
        except Transaction.DoesNotExist:
            return self.send_response(0, "Transaction not created.")
        final_price = transaction.final_price
        user = transaction.buyer
        cart = user.cart
        # price = cart.total_price_with_shipping_charge()
        # if apply_zapcash == 'apply_zapcash':
        #     wallet_amount = int(cart.user.get_zap_wallet)
        #     lp = cart.total_listing_price()
        #     if wallet_amount > lp:
        #         wallet_amount = lp
        #     zap_algo_return = self.zapcash_algo(
        #         wallet_amount, price)
        #     final_price = zap_algo_return['total_amount']
        #     wallet_to_use = zap_algo_return['zapwallet']
        # else:
        #     final_price = price
        #     wallet_to_use = 0

        bill = zap_bill_generator(request, final_price, txn_id=transaction.transaction_ref,  action_from='android')
        # data={
        #     'buyer': user,
        #     'transaction_ref': bill['merchantTxnId'],
        #     'zapwallet_used': wallet_to_use,
        #     'consignee': cart.delivery_address.id
        # }
        # transaction, valid = create_transaction(user, data)
        # if not valid:
        #     return self.send_response(0, transaction)
        if settings.CELERY_USE:
            for i in cart.item.all():
                zap_reduce_quantity(i.product.id, i.size.id, i.quantity)
            product_increase_quantity.apply_async((bill['merchantTxnId'],), countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)

        zaplogging.delay("android-dup"+str(bill)) if settings.CELERY_USE else zaplogging("android-dup"+str(bill))
        return JsonResponse(bill)

class CodGenerator(ZapAuthView):
    def zapcash_algo(self, zapwallet, total_amount):
        if zapwallet >= total_amount:
            zapwallet_used = total_amount
            total_amount = 0
        else:
            total_amount -= zapwallet
            zapwallet_used = zapwallet
        return {'zapwallet': zapwallet_used, 'total_amount': total_amount}

    def get(self,request, apply_zapcash=None, format=None):
        cart = request.user.cart
        wallet_amount = int(request.user.get_zap_wallet)
        if apply_zapcash=='apply_zapcash':
            wallet_to_use = zap_algo_return['zapwallet']
        else:
            wallet_to_use = 0
        if cart.total_price_with_shipping_charge() > 90000:
            return self.send_response(0, "COD not available above Rs. 90000")
        cod_status = make_cod_transaction(cart, wallet_to_use, request)
        return self.send_response(1, cod_status)

def cart_from_transaction(tr_id):
    try:
        transaction = Transaction.objects.get(transaction_ref=tr_id)
        srl = TransSrlzr(transaction)
        print srl.data
        return self.send_response(1, srl.data)
    except Transaction.DoesNotExist:
        return {}
class PaymentSummary(ZapAuthView):

    def get(self, request, format=None):
        if request.GET.get('txid', ''):

            try:
                transaction = Transaction.objects.get(transaction_ref=request.GET[
                                                      'txid'])
                if transaction.status in ['success','pending']:
                    srl = TransSrlzr(transaction)
                else:
                    srl = CartSerializerForTransaction(request.user.cart, context={'zapwallet_used': transaction.zapwallet_used})
                return self.send_response(1, srl.data)
            except Transaction.DoesNotExist:
                return self.send_response(0, 'no permission')
        else:
            transactions = Transaction.objects.filter(
                success=True, cart__user=request.user).order_by('-id')
            srl = GetTransactionSerializer(transactions, many=True)
            print '&' * 10
            print srl.data, 'data'
            return self.send_response(1, srl.data)

from django.utils import timezone
class RetryPayment(ZapAuthView):
    def post(self, request, tx_id, format=None):
        try:
            trans = Transaction.objects.get(buyer=request.user,transaction_ref=tx_id)
        except Transaction.DoesNotExist:
            return self.send_response(0, 'transaction not found')
        if int(trans.zapwallet_used):
            wallet_amount = int(request.user.get_zap_wallet)
            if trans.zapwallet_used > wallet_amount:
                return self.send_response(0, 'You don"t have ZapCash to retry this payment.')
        cart = request.user.cart
        if not checkCartAvailibility(cart.id):
            return self.send_response(0, "Products available is changed in cart.")
        cod = request.data.get('cod', False)
        if cod and cart.total_price_with_shipping_charge() > 90000:
            return self.send_response(0, "COD not available above Rs. 90000")
        trans.pk = None
        trans.status = None
        txn_id_new = str(int(time.time())) + str(random.randint(10000, 99999))
        trans.transaction_ref = txn_id_new
        trans.save()

        if cod:
            return self.send_response(1, make_cod_transaction(cart, trans.zapwallet_used, request))
        final_price = cart.total_price_with_shipping_charge()
        final_price = final_price - trans.zapwallet_used
        if final_price > 0:  # if payamount is in zapcash
            bill = zap_bill_generator(request, final_price, txn_id_new, action_from='website')
            bill['message'] = 'TXFWD'
            bill['transaction_ref'] = txn_id_new
            if settings.CELERY_USE:
                for i in request.user.cart.item.all():
                    zap_reduce_quantity(i.product.id, i.size.id, i.quantity)
                product_increase_quantity.apply_async((bill['merchantTxnId'],), countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)
            return self.send_response(1, bill)
        else:
            make_order(trans, cart)
            trans.status = 'success'
            trans.save()
            send_email_after_order_success(request, request.user, trans.zapwallet_used)
            return self.send_response(1, {'transaction_id': txn_id_new, 'message': 'TXSUCCESS'})

import json
import urllib2
class JuspayWebsiteReturnUrl(ZapView):

    def get(self, request, format=None):
        # pdb.set_trace()
        data = request.GET.copy()
        zaplogging.delay("website" + str(data)) if settings.CELERY_USE else zaplogging("website" + str(data))
        transaction = Transaction.objects.get(
            transaction_ref=data['order_id'])
        buyer = transaction.buyer
        if buyer.cart.total_price_with_shipping_charge() == transaction.zapwallet_used + transaction.final_price and (timezone.now() - transaction.time).seconds/60 < 11:#signature == data["signature"]:
            if data['status_id'] == '21':
                transaction.status = 'success'
                transaction.save()
                make_order(transaction, buyer.cart)
                save_payment_response_juspay(transaction, data, True)
                send_email_after_order_success(request, buyer.cart, transaction.zapwallet_used)
            elif data['status_id'] == '23':
                transaction.status = 'pending'
                transaction.save()
                make_order(transaction, buyer.cart)
                save_payment_response_juspay(transaction, data, False)
                if settings.CELERY_USE:
                    check_pending_transaction.apply_async(args=[transaction.id], countdown=settings.ITEM_INCREASE_AFTER_PAYMENT_FAIL_TIME)
                else:
                    check_pending_transaction(transaction.id)
            else:
                if settings.CELERY_USE:
                    product_increase_quantity(transaction.transaction_ref)
                transaction.status = 'failed'
                transaction.save()
                save_payment_response_juspay(transaction, data, False)
                context = {'data': dict(request.data)}
                print "Transaction Failed"
                if request.PLATFORM == 'WEBSITE':
                    r_url = "/order/" + str(data['order_id'])
                    return HttpResponseRedirect(r_url)
                return self.send_response(0)
        else:
            if settings.CELERY_USE:
                product_increase_quantity(transaction.transaction_ref)
            if data['status_id'] == '21':
                print "Payment is success, send mail to admins"
                zapemail = ZapEmail()
                zapemail.send_email("","Check Transaction id : {}".format(transaction.id), "","hello@zapyle.com", "shafi@zapyle.com")              

            transaction.status = 'sig_mismatch'
            transaction.save()
            save_payment_response_juspay(transaction, data, False)
            context = {'data': dict(request.data)}
            context = {'data': "error"}
        if request.PLATFORM == 'WEBSITE':
            r_url = "/order/" + str(data['order_id'])
            return HttpResponseRedirect(r_url)
        return self.send_response(1)
        

def save_payment_response_juspay(transaction,data,status):
    payment_serializer = PaymentResponseSerializer(
        data={
            'transaction': transaction.id,
            'payment_success': status,
            'payment_id': data.get('transactionId'),
            'payment_transaction_id': data['order_id'],
            # 'pg_transaction_id': data['pgTxnNo'],
            # 'marketplaceTxId': data.get('marketplaceTxId',''),
            # 'transaction_ref_id': data['TxRefNo'],
            'status': data['status'],
            # 'payment_gateway': data['TxGateway'],
            # 'amount': data['amount'],
            # 'payment_mode': data['paymentMode'],
            # 'currency': data['currency'],
            # 'payment_time': data['txnDateTime'],
            'whole_response': dict(data),
            # 'issuer_ref_no': data['issuerRefNo'],
            # 'auth_id_code': data['authIdCode'],
            # 'currency': data['currency'],
            'merchant_transaction_id': data['order_id']})

    if payment_serializer.is_valid():
        paymentlog = payment_serializer.save()
    return True

# def make_order(transaction, cart):
#     for item in cart.item.all():
#         order_number = "OD" + "%.3f" % round(time.time(), 3)
#         order_number = order_number.replace('.', '')
#         op = make_orderered_product(item)

#         print (item.price()/cart.total_price_with_shipping_charge())*transaction.zapwallet_used
#         print item.price(), cart.total_price_with_shipping_charge(), transaction.zapwallet_used
#         data={
#             'shipping_charge': settings.SHIPPING_CHARGE if item.product.listing_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0,
#             'product': item.product.id,
#             'transaction': transaction.id,
#             'order_number': order_number,
#             'ordered_product': op.id,
#             'quantity': item.quantity,
#             'consignor': item.product.pickup_address.id,
#             'zapwallet_used': (item.price()/cart.total_price_with_shipping_charge())*transaction.zapwallet_used
#         }
#         if transaction.status == 'pending':
#             data['order_status'] = 'pending'
#         if item.product.with_zapyle:
#             data['confirmed_with_seller'] = True
#         serializer = OrderSerializer(data=data)
#         if not serializer.is_valid():
#             print serializer.errors
#             return None
#         srlzr = serializer.save()
#         no_of_prod = item.product.product_count.get(size=item.size)
#         no_of_prod.quantity -= item.quantity
#         no_of_prod.save()
#         OrderTracker.objects.create(orders_id=srlzr.id,status="being_confirmed")
#     if not transaction.status == 'pending':
#         success_order_follow_up(transaction)
