# encoding=utf8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer

from zap_apps.payment.models import ZapWallet
from django.db.models import Sum
from zap_apps.zapuser.models import ZapUser
import json
from zap_apps.zap_notification.tasks import zaplogging
from zap_apps.zap_notification.views import PushNotification 
pushnots = PushNotification()


class AppViralityConversion(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        print type(data)
        print data
        zaplogging.delay("appvirality-conversion"+str(data)) if settings.CELERY_USE else zaplogging("appvirality-conversion"+str(data))
        if data['securekey'] == settings.PRIVATE_KEY:
            # if data["success"] == True and data['eventname'] == "ZapSignup":
            #     friend = data['friend']
            #     try:
            #         u = ZapUser.objects.get(email=friend['emailid'])
            #     except ZapUser.DoesNotExist:
            #         try:
            #             u = ZapUser.objects.get(zap_username=friend['storeuserid'])
            #         except:
            #             return self.send_response(0, "Failed")
            #     u.issue_zap_wallet(data['amount'], mode='0' ,purpose="ZapSignup Appvirality Friend")
            if data["success"] == True:
                referrer = data['referrer']
                try:
                    u = ZapUser.objects.get(email=referrer['emailid'])
                except ZapUser.DoesNotExist:
                    try:
                        u = ZapUser.objects.get(zap_username=referrer['storeuserid'])
                    except:
                        return self.send_response(0, "Failed")
                friend = data['friend']
                try:
                    f = ZapUser.objects.get(email=friend['emailid'])
                except ZapUser.DoesNotExist:
                    try:
                        f = ZapUser.objects.get(zap_username=friend['storeuserid'])
                    except:
                        return self.send_response(0, "Failed")
                if data['eventname'] == "ZapSignup":
                    msg = "Guess what? {} has signed up to Zapyle thanks to you, so get ready to be credited with Rs. 100 as soon as she updates her Closet or shops! ".format(f.zap_username)
                    pushnots.send_notification(u, msg, extra={'action': 'referrel', 'msg': msg, 'marketing': '1'})
                if data['eventname'] == "BuyOrSell":
                    if data['extraInfo'] == "Sell":
                        msg = "Congrats Zapyler! Your referral {} just posted their first Closet item, Rs. 100 will be added to your Zapcash within an hour. Thanks!".format(f.zap_username)
                    if data['extraInfo'] == "Buy":
                        msg = "Congrats Zapyler! Your referral {} just made their first purchase, Rs. 100 will be added to your Zapcash within an hour. Thanks a lot!".format(f.zap_username)
                    pushnots.send_notification(u, msg, extra={'action': 'referrel', 'msg': msg, 'marketing': '1'})

        return self.send_response(1, "Yeah, Success")


class AppViralityFriendReward(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        print type(data)
        print data
        zaplogging.delay("appvirality-friendreward"+str(data)) if settings.CELERY_USE else zaplogging("appvirality-friendreward"+str(data))

        if data['securekey'] == settings.PRIVATE_KEY:
            if data["success"] == True and data['eventname'] == "ZapSignup":
                friend = data['friend']
                try:
                    u = ZapUser.objects.get(email=friend['emailid'])
                except ZapUser.DoesNotExist:
                    try:
                        u = ZapUser.objects.get(zap_username=friend['storeuserid'])
                    except:
                        return self.send_response(0, "Failed")
                u.issue_zap_wallet(int(friend['amount']), mode='0' ,purpose="ZapSignup Appvirality Friend")
                msg = "Congrats Zapyler!, You just earned Rs. 100. Use it well!"
                pushnots.send_notification(u, msg, extra={'action': 'referrel', 'msg': msg, 'marketing': '1'})

        return self.send_response(1, "Yeah, Success")


class AppViralityReferrerReward(ZapView):
    def post(self, request, format=None):
        data = request.data.copy()
        print type(data)
        print data
        zaplogging.delay("appvirality-referrelreward"+str(data)) if settings.CELERY_USE else zaplogging("appvirality-referrelreward"+str(data))

        if data['securekey'] == settings.PRIVATE_KEY:
            try:
                u = ZapUser.objects.get(email=data['emailid'])
            except ZapUser.DoesNotExist:
                try:
                    u = ZapUser.objects.get(zap_username=data['storeuserid'])
                except:
                    return self.send_response(0, "Failed")
            u.issue_zap_wallet(settings.REFERRER_AMOUNT, mode='0' ,purpose="Appvirality Reward referrer")
            # msg = "Congrats Zapyler! You just earned Rs. 200. Use it well!"
            # pushnots.send_notification(u, msg, extra={'action': 'referrel', 'msg': msg, 'marketing': '1'})
        return self.send_response(1, "Yeah, Success")


class AppViralityCampaign(ZapView):
    def get(self, request, format=None):
        if request.user.is_authenticated():
            zapwallet_used_objects = ZapWallet.objects.filter(
                user=request.user, credit=False)
            zapwallet_earned_objects = ZapWallet.objects.filter(
                user=request.user, credit=True)
            balance = (zapwallet_earned_objects.aggregate(Sum('amount'))['amount__sum'] or 0) - (zapwallet_used_objects.aggregate(Sum('amount'))['amount__sum'] or 0)
            
        else:
            balance = 0
        return self.send_response(1, {
            'referrer_amount': settings.REFERRER_AMOUNT, 
            'friend_amount': settings.FRIEND_AMOUNT,
            'zapcash': balance
            })