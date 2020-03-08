from django.shortcuts import render
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from zap_apps.offer.models import ZapOffer
from zap_apps.extra_modules.appvirality import AppViralityApi
from zap_apps.zapuser.models import AppViralityKey
from django.conf import settings
# Create your views here.


class ApplyOffer(ZapView):

    def post(self, request, offer_id, format=None):
        try:
            if unicode(offer_id).isdigit():
                offer = ZapOffer.objects.get(id=offer_id)
            else:
                offer = ZapOffer.objects.get(code=offer_id)
            if offer.offer_on == 'PRODUCT':
                from zap_apps.zap_catalogue.models import ApprovedProduct
                post_data = request.data.copy()
                if 'products' in post_data:
                    offers_applied = {}
                    try:
                        products = ApprovedProduct.objects.filter(id__in=post_data['products'])
                        for product in products:
                            if request.user.is_authenticated():
                                applicable = offer.is_applicable(product.id, request.user.id)
                            else:
                                applicable = offer.is_applicable(product.id)
                            if applicable['status']:
                                offers_applied.update({product.id: {'applied': True, 'offer_price':product.get_offer_price(offer.id)}})
                                # return self.send_response(1, {'offer_price':product.get_offer_price(offer.id)})
                            else:
                                offers_applied.update({product.id: {'applied': False, 'error': applicable['error']}})
                                # return self.send_response(0, applicable.error)
                        return self.send_response(1, offers_applied)
                    except Exception:
                        return self.send_response(0, 'Sorry! No such offer exists.')
                elif 'carts' in post_data:
                    from zap_apps.cart.models import Item
                    try:
                        cart_items = Item.objects.filter(id__in=post_data['carts'])
                        offers_applied = {}
                        offerapplied = False
                        error = ''
                        for item in cart_items:
                            product = item.product
                            if request.user.is_authenticated():
                                applicable = offer.is_applicable(product.id, request.user.id)
                            else:
                                applicable = offer.is_applicable(product.id)
                            if applicable['status']:
                                item.offer = offer
                                item.save()
                                offerapplied = True
                                offers_applied.update({item.id: {'applied': True, 'offer_price': product.get_offer_price(offer.id)}})
                            else:
                                error = applicable['error']
                                offers_applied.update({item.id: {'applied': False, 'error': applicable['error']}})
                        if offerapplied:
                            return self.send_response(1, offers_applied)
                        else:
                            return self.send_response(0, 'Sorry the offer could not be applied. ' + error)
                    except Exception:
                        return self.send_response(0, 'Sorry! No such offer exists.')
            elif offer.offer_on == 'CART':
                from zap_apps.cart.models import Item, Cart
                if request.user.is_authenticated():
                    try:
                        cart = Cart.objects.get(user=request.user.id)
                        applicable = offer.is_applicable(user_id=request.user.id)
                        if applicable['status']:
                            cart.offer = offer
                            cart.save()
                            return self.send_response(1, {'offer_benefit': cart.zapyle_discount()})
                        else:
                            return self.send_response(0, 'Sorry the offer could not be applied. ' + applicable['error'])
                    except Exception as e:
                        return self.send_response(0, 'Sorry the offer could not be applied. ' + e.message)
                else:
                    return self.send_response(0, 'Please login to apply the offer.')
        except Exception as e:
            return self.send_response(0, 'Sorry! No such offer exists. ' + e.message)


def apply_listing_offers(product=None, user=None):
    for i in ZapOffer.objects.filter(offer_when="LISTING"):
        if i.offer_available():
            if i.offer_benefit.type == "CREDIT":
                user.issue_zap_wallet(i.offer_benefit.value,mode='0',purpose="credit when listing")
            if i.offer_benefit.type == "PERCENTAGE_COMMISSION":
                product.percentage_commission = i.offer_benefit.value
                product.save()

def apply_signup_offers(product=None, user=None):
    for i in ZapOffer.objects.filter(offer_when="SIGNUP"):
        if i.offer_available():
            if i.offer_benefit.type == "CREDIT":
                user.issue_zap_wallet(i.offer_benefit.value,mode='0',purpose="credit when signup")
            elif i.offer_benefit.type == 'ABS_DISCOUNT':
                if i.offer_condition:
                    from django.http import QueryDict
                    from zap_apps.filters.filters_common import cache_sort
                    from zap_apps.zapuser.models import ZapUser, UserGroup
                    if i.offer_condition.user_filter:
                        filter = i.offer_condition.user_filter
                        filter_params = QueryDict(filter[unicode(filter).index('?') + 1:])  # remove ? and the part before that - send only the query part
                        filter_dict = cache_sort(filter_params)
                        filter_dict.pop('initial_filters')
                        if 'user_group' in filter_dict.keys():
                            user_group = UserGroup.objects.get(id=filter_dict['user_group'][0])
                            user_group.zapyle_users.add(user)
                            user_group.save()


def apply_app_signup_offers(product=None, user=None):
    for i in ZapOffer.objects.filter(offer_when="APP_SIGNUP"):
        if i.offer_available():
            if i.offer_benefit.type == "CREDIT":
                if user.logged_device.name in ["ios", 'android']:
                    user.issue_zap_wallet(i.offer_benefit.value,mode='0',purpose="credit when app signup")

def apply_website_signup_offers(product=None, user=None):
    for i in ZapOffer.objects.filter(offer_when="WEBSITE_SIGNUP"):
        if i.offer_available():
            if i.offer_benefit.type == "CREDIT":
                if user.logged_device.name == "website":
                    user.issue_zap_wallet(i.offer_benefit.value,mode='0',purpose="credit when website signup")
            # if i.offer_benefit.type == "PERCENTAGE_COMMISSION":
            #     product.percentage_commission = i.offer_benefit.value
            #     product.save()


def apply_offers(when, product=None, user=None):
    if when == "LISTING":
        apply_listing_offers(product=product, user=user)
    if when == "SIGNUP":
        apply_signup_offers(product=product, user=user)
    if when == "APP_SIGNUP":
        apply_app_signup_offers(product=product, user=user)
    if when == "WEBSITE_SIGNUP":
        apply_website_signup_offers(product=product, user=user)
