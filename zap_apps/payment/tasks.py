from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from celery import task
from django.conf import settings
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from zap_apps.payment.models import ZapWallet
from zap_apps.order.models import Order, Return, Transaction
from zap_apps.logistics.tasks import decryptAcc
from django.utils import timezone
import requests
import pdb


@task
def product_increase_quantity(t_ref):
	trans = Transaction.objects.get(transaction_ref=t_ref)
	if not trans.status:
		from zap_apps.payment.views import zap_increase_quantity
		for i in trans.buyer.cart.item.all():
			zap_increase_quantity(i.product, i.size, i.quantity)
# @periodic_task(run_every=(crontab(minute=30, hour=2)))
def refund():

    returns = Return.objects.filter(refund_mode='account_transfer', credited=False)

    zapemail = ZapEmail()
    for ret in returns:
        order = ret.order_id
        # returns = order.returnmodel
        buyer = order.transaction.buyer
        # credited =False
        # if order.final_payable_price:
        if order.transaction.payment_mode == 'cod':
            userdata = buyer.user_data
            if userdata.account_number and userdata.account_holder and userdata.ifsc_code:
                email_body = "Greetings,\n\nPlease make a payment for returns to the below given buyer.\n\nAccount Holder Name: "+userdata.account_holder+"\nAccount Number: "+decryptAcc(userdata.account_number)+"\nIFSC No.: "+userdata.ifsc_code+"\nAmount: "+str(order.final_payable_price)
                zapemail.send_email_attachment(Refund+" Order - : "+order.order_number,settings.FROM_EMAIL,['shafi@zapyle.com'],email_body=email_body) #,'accounts@zapyle.com', 'likhita@zapyle.com'
                order.refund_status = 'initiated'
                order.save()
            #send email to accounts
            else:
                print 'Not Successful'
                #send them email
        else:
            payment_resp = order.transaction.payment_resp
            refund_data = {'merchantTxnId': payment_resp.merchant_transaction_id, 'pgTxnId': payment_resp.pg_transaction_id, 
                'rrn':payment_resp.issuer_ref_no, 'authIdCode':payment_resp.auth_id_code, 'currencyCode': payment_resp.currency, 
                'amount':order.final_payable_price(), 'txnType':'Refund'}
            acc_refund = citrus_refund(refund_data)
            if acc_refund:
                order.refund_status = 'refunded'
                order.save()




def check_refund_initiate():
    Q1 = Q(order_id__refund_status__isnull=True)
    Q2 = Q(refund_mode__isnull=True)
    Q3 = Q(order_id__order_status='returned') 
    past_date = timezone.now() - timezone.timedelta(2)
    Q4 = Q(last_communication__isnull=True)
    Q4 |= Q(last_communication__lte=past_date)
    
    returns = Return.objects.filter(Q1 & Q2 & Q3 & Q4)
    for ret in returns:
        print 'dummy'
        #send notif and email




@task
def check_pending_transaction(transaction_id):
    # pdb.set_trace()
    from zap_apps.payment.views import success_order_follow_up, send_email_after_delayed_order_success
    transaction = Transaction.objects.get(id=transaction_id)
    payment_resp = transaction.payment_response.all()[0]
    url = settings.CITRUS_ENQUIRY_URL + payment_resp.payment_transaction_id
    headers = {'access_key':settings.MERCHANT_ACCESS_KEY, 'secret_key':settings.MERCHANT_SECRET_KEY, 'Accept':'application/json'}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        json_response = resp.json() 
        all_enquiry = json_response['enquiryResponse']
        latest_enquiry = all_enquiry[len(all_enquiry)-1]
        if int(latest_enquiry['respCode']) in [0,14]:
            #SUCCESS
            transaction.status = 'success'
            transaction.save()
            payment_resp.payment_success = True
            payment_resp.status = 'SUCCESS_ON_VERIFICATION'
            payment_resp.save()
            success_order_follow_up(transaction)
            send_email_after_delayed_order_success(transaction)

        elif int(latest_enquiry['respCode']) == 4:
            #hit again
            if settings.CELERY_USE:
                check_pending_transaction.apply_async(args=[transaction.id], countdown=6000)
            else:
                check_pending_transaction(transaction.id)
        else:
            #Failed
            transaction.status = 'failed'
            transaction.save()
            orders = transaction.order.all()
            for order in orders:
                order.order_status = 'failed'
                order.save()
            #communication





