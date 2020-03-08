from celery import task
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
import requests
from pushbots import Pushbots
from django.conf import settings
import random
from zap_apps.order.models import Order
import locale
from django.template import Context
from django.template.loader import render_to_string
# from zap_apps.zap_notification.views import ZapEmail
import pdb
from zap_apps.extra_modules.slack import Slack
#not used
@task
def zap_cash_task(url, data, headers, amount, credit, user_id=None, tr_ref_id=None):
    # from zap_apps.payment.views import ZapCash
    from zap_apps.zapuser.models import ZapUser
    response = requests.post(
        url=url, data=data, headers=headers, verify=False)
    # try:
    # 	if response.json()['d']['status']['StatusID'] == "1":
    #         # ZapCash.objects.create(user_id=user_id, 
    #         	# credit=credit, tr_ref_id=tr_ref_id, amount=amount, status=True)
    # 	else:
    #         # ZapCash.objects.create(user_id=user_id, 
    #         # 	credit=credit, tr_ref_id=tr_ref_id, amount=amount, status=False)
    # except:
    # 	if response.json()['d']['status']['StatusID'] == "1":
    #         # ZapCash.objects.create(user_id=user_id, 
    #         # 	credit=credit, tr_ref_id=tr_ref_id, amount=amount, status=False)
    return response.text


@task
def zap_cash_task1(amount, credit, mode='0', user_id=None ,purpose=None, transaction=None, return_id=None, promo=None):
    from zap_apps.payment.models import ZapWallet
    
    ZapWallet.objects.create(amount=amount, credit=credit, user=user_id,transaction=transaction, purpose=purpose, mode=mode, return_id=return_id,promo=promo)
   
    return "Successfully Done"

# def zap_cash_task1(amount, credit, user_id=None, transaction=None, return_id=None):
#     # pdb.set_trace()
#     # from zap_apps.payment.views import ZapCash
#     from zap_apps.payment.models import ZapWallet
#     from zap_apps.zapuser.models import ZapUser
#     # response = requests.post(
#     #     url=url, data=data, headers=headers, verify=False)
#     # try:
#     #     if response.json()['d']['status']['StatusID'] == "1":
#     if transaction:
#         ZapWallet.objects.create(user_id=user_id, 
#         credit=credit, amount=amount, transaction=transaction)
#     elif return_id:
#         ZapWallet.objects.create(user_id=user_id, 
#         credit=credit, amount=amount, return_id=return_id)
#     else:
#         ZapWallet.objects.create(user_id=user_id, 
#         credit=credit, amount=amount)
    
#         # else:
#         #     ZapCash.objects.create(user_id=user_id, 
#         #         credit=credit, tr_ref_id=tr_ref_id, amount=amount, status=False)
#     # except:
#     #     if response.json()['d']['status']['StatusID'] == "1":
#     #         ZapCash.objects.create(user_id=user_id, 
#     #             credit=credit, tr_ref_id=tr_ref_id, amount=amount, status=False)
#     return "Successfully Done"



@task
def seller_address_conf_after_order(order_id):
    from zap_apps.zap_notification.views import ZapEmail
    zapemail = ZapEmail()
    order = Order.objects.get(id=order_id)
    if not order.ordered_product.with_zapyle:
        # protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        productLink =  settings.CURRENT_DOMAIN + '/#/product/' + str(order.product.id)
        # img = 
        img =  settings.CURRENT_DOMAIN+ order.ordered_product.image.image.url_500x500
        # img =  protocol + '://'+settings.LOGISTICS_IMG_DOMAIN+ order.product.images.all()[0].image.url_500x500
        
        productSize = order.ordered_product.size
        productQuantity = order.quantity
        total_order_price = locale.format(
                            "%.2f", order.final_price, grouping=True)
        productPrice = str(total_order_price)
        if order.product.user.user_data.account_holder:
            accountDecider = 0
        else:
            accountDecider = 1
        # ##pdb.set_trace()
        html = settings.SELLER_ADDRESS_CONF_AFTER_ORDER
        template_data = {'seller_name': order.consignor.user.get_full_name(), 
        'from_name': order.consignor.name, 'from_add': order.consignor.address, 
        'from_city': order.consignor.city, 'from_state': order.consignor.state.name,
        'from_pincode':order.consignor.pincode, 'from_country':order.consignor.country, 
        'productLink':productLink, 'img':img, 'productName':order.ordered_product.title, 'productQuantity':productQuantity,  
        'productSize':productSize,'productColor': order.ordered_product.color if order.ordered_product.color else "Not available",
        'productPrice':productPrice, 'accountDecider':accountDecider}

        
        html_body = render_to_string(html['html'], template_data)
        zapemail.send_email_alternative(html[
                            'subject'], settings.FROM_EMAIL, order.consignor.user.email, html_body)
    slack = Slack()
    slack.post_msg(
        "*{}*".format("Yay! Got an Order."), 
        order.product.images.all().order_by('id')[0].image.url_1000x1000,
        "https://www.zapyle.com/zapstatic/frontend/favicon.ico", 
        "*{} for {} at {} ({})* -- {}".format('Yay! Got an order', order.product.title, order.product.listing_price, order.transaction.final_price, 'https://www.zapyle.com/product/{}'.format(order.product.id)),
        )

        # msg = EmailMultiAlternatives(subject="Yay! Your Deal's Gone Through on Zapyle!.",
        #                              from_email="hello@zapyle.com", to=[order.consignor.user.email], body=html_body)
        # msg.attach_alternative(html_body, "text/html")
        # msg.send()





   