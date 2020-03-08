import json
import sys,os,csv
import django
try:
    env = sys.argv[1]
except IndexError:
    raise Exception("Please provide settings [local/ staging/ prod]")

os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.{}".format(env)
django.setup()

from zap_apps.order.models import *
with open('order.json') as f:
    res = json.loads(f.read())
orders = [i for i in res if '.order' in i['model']]
transactions = [i for i in res if 'transaction' in i['model']]
Transaction.objects.filter(order__isnull=True).update(deleted=True)
for i in orders:

    t_id = i['fields']['transaction']
    try:
        t2 = Transaction.objects.get(id=t_id)
    except Transaction.DoesNotExist:
        continue
    print t2
    for j in transactions:
        if j['fields']['transaction_ref'] == t2.transaction_ref:
            t1 = j['fields']
            break
    o1 = i['fields']
    try:
        o2 = Order.objects.get(id=i['pk'])
    except Order.DoesNotExist:
        continue
    if t1['cod'] == True:
        t2.payment_mode='cod'
    t2.status = 'success'
    t2.zapwallet_used = int(t1['zapcash_used']) + int(t1['zapcredit_used']) + int(t1.get('discount', 0))
    if t1['initiate_payout'] and t1['paid_out']:o2.payout_status='paid_out'
    if t1['initiate_payout'] == True and t1['paid_out'] == False:o2.payout_status='can_initiate_payout'
    if int(t1.get('discount', 0)): t2.buyer.issue_zap_wallet(int(t1['discount']), purpose="During migration"), t2.buyer.redeem_zap_wallet(int(t1['discount']),purpose="During migration")
    t2.consignee_id = o1['consignee']
    if o1['confirmed_with_buyer'] and o1['confirmed_with_seller'] and \
        o1['triggered_logistics']==False and o1['returned'] == False and o1['cancelled']==False:
        o2.order_status = 'confirmed'
    if (o1['confirmed_with_buyer']==False or o1['confirmed_with_seller']==False) and \
        o1['returned'] == False and o1['cancelled']==False:
        o2.order_status = 'being_confirmed'
    if o1['delivery_date']:o2.order_status = 'delivered'
    if o1['cancelled'] == True: o2.order_status = 'cancelled'
    print(j['pk'], int(t1['zapcash_used']) + int(t1['zapcredit_used']) + int(t1.get('total_discount', 0))),">>>>"

    o2.zapwallet_used = int(t1['zapcash_used']) + int(t1['zapcredit_used']) + int(t1.get('total_discount', 0))
    t2.zapwallet_used = int(t1['zapcash_used']) + int(t1['zapcredit_used']) + int(t1.get('total_discount', 0))
    try:
        t2.save()
    except:
        pass
    try:
        o2.save()
    except:
        pass