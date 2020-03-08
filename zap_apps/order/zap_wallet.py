import requests
from django.conf import settings
import json
from django.db.models import F
from zap_apps.payment.models import ZapWallet
from zap_apps.order.tasks import zap_cash_task, zap_cash_task1
import pdb






class ZapWalletView(object):

    def issue(self, amount, mode='0', user_id=None ,purpose=None, return_id=None, promo=None):
        if settings.CELERY_USE:
            zap_cash_task1.delay(amount, credit=True, mode=mode, user_id=user_id ,purpose=purpose, return_id=return_id, promo=promo)
        else:
            zap_cash_task1(amount, credit=True, mode=mode, user_id=user_id ,purpose=purpose, return_id=return_id, promo=promo)


    def redeem(self, amount, mode='0', user_id=None, purpose=None, transaction=None):
        
        if settings.CELERY_USE:
            zap_cash_task1.delay(amount, credit=False, mode=mode, user_id=user_id ,purpose=purpose, transaction=transaction)
        else:
            zap_cash_task1(amount, credit=False, mode=mode, user_id=user_id ,purpose=purpose, transaction=transaction)

    def balance(self,user):
        #USE 
        # pdb.set_trace()
        bal = (ZapWallet.objects.filter(user=self, credit=True).aggregate(s=Sum(F('amount')))['s'] or 0) - (ZapWallet.objects.filter(user=self, credit=False).aggregate(s=Sum(F('amount')))['s'] or 0)
        if bal >= 0:
            return {
                'status': "success",
                'amount':  bal}
        else:
            return {'status': "error", "data": "Something went wrong!"}
