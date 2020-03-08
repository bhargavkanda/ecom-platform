from django.shortcuts import render
from zap_apps.cart.models import Cart, Item
from zap_apps.coupon.models import Coupon, PromoCode
from django.utils import timezone
from zap_apps.cart.cart_serializers import CartSerializer
from zap_apps.account.zapauth import ZapView, ZapAuthView
from zap_apps.order.models import Order, Transaction
from zap_apps.payment.models import ZapWallet
from collections import Counter
import pdb


# Create your views here.


class Coupons(ZapAuthView):
    def get_coupon_price(self, coupon, total_price):
        if coupon.abs_discount:
            discount = coupon.abs_discount
        elif coupon.perc_discount:
            discount = (coupon.perc_discount * total_price) / 100
        discount = min(discount, coupon.max_discount or discount)

        return discount

    



    def post(self, request, format=None):
        '''
            Apply coupon to cart if possible.
        '''
        cart = Cart.objects.get(user=request.user, success=False)
        # import pdb; #####pdb.set_trace()

        transaction_ids = Order.objects.all().values_list('transaction', flat=True)
        no_user_cart_ids = Transaction.objects.filter(id__in=transaction_ids).values_list('cart', flat=True)

        cart_ids = Transaction.objects.filter(id__in=transaction_ids, buyer=request.user).values_list('cart', flat=True)


        
        # total_price = 0
        # for item in cart.items.all():
        #     total_price += item.product.listing_price + item.product.shipping_charge
        total_price = cart.total_price
        try:
            coupon = Coupon.objects.get(
                coupon_code=request.data['coupon_code'])

            no_user_coupons_carts = Cart.objects.filter(id__in=no_user_cart_ids, coupon=coupon)
        except Coupon.DoesNotExist:
            return self.send_response(0, "Sorry, Invalid Coupon")
        except KeyError:
            return self.send_response(0, "Please enter coupon code.")
        if coupon.valid_from < timezone.now() < coupon.valid_till:
            if coupon.allowed_users.all() and not (request.user in coupon.allowed_users.all()):
                return self.send_response(0, "Sorry, Invalid Coupon")

            if coupon.allowed_usage:
                if not coupon.allowed_users.all() and coupon.allowed_usage <= len(no_user_coupons_carts):
                    return self.send_response(0, 'Sorry! This Coupon has expired.')
                carts = Cart.objects.filter(id__in=cart_ids,coupon=coupon)
                if coupon.allowed_usage <= len(carts):
                    return self.send_response(0, 'Sorry! This Coupon has expired.')
                if coupon.allowed_per_user and coupon.allowed_per_user <= len(carts):
                    return self.send_response(0, 'Sorry! This Coupon has expired.')

            if total_price >= coupon.min_purchase:
                if request.data.get('zapcash_used'):
                    if self.get_coupon_price(coupon, total_price) > (total_price-request.data['zapcash_used']):
                        return self.send_response(0, 'Sorry! This coupon discount is greater than final price.') 
                if self.get_coupon_price(coupon, total_price) > total_price:
                    return self.send_response(0, 'Sorry! This coupon discount is greater than final price.')

                # if coupon.abs_discount:
                #     total_discount = coupon.abs_discount
                # else:
                #     disc = (coupon.perc_discount * total_price) / 100
                #     if coupon.max_discount:
                #         if (disc < coupon.max_discount):
                #             total_discount = round((total_price - disc),0)
                #         else:
                #             total_discount = round((total_price - max_discount),0)
                #     else:
                #         total_discount = round((total_price - disc),0)

                # final_price = total_price - total_discount

                cart.coupon = coupon
                cart.save()
                final_price = cart.cart_price_after_coupon
                return self.send_response(1, {'final_price': final_price, 'title': coupon.coupon_code, 'coupon_discount': cart.get_coupon_discount})
            else:
                return self.send_response(0, 'Uh oh! You must shop for at least Rs. {}'.format(coupon.min_purchase))
        else:
            return self.send_response(0, 'Sorry! This coupon has expired.')



class Promo(ZapAuthView):

    def get_promo_amount(self,promo):
        if promo.abs_amount:
            amount = promo.abs_amount
        return amount

    def post(self, request, format=None):
        '''
        Apply Promo Code
        '''
        # pdb.set_trace()
        promo_wallet = ZapWallet.objects.filter(mode='1', credit=True)
        user_promo = promo_wallet.filter(user=request.user.id)


        try:
            promo = PromoCode.objects.get(
                code=request.data['code'])
        except PromoCode.DoesNotExist:
            return self.send_response(0, "Sorry, Invalid Promo Code.")

        if promo.valid_from < timezone.now() < promo.valid_till:
            user_promo_dict = Counter(user_promo.values_list('promo', flat=True))
            current_promo = promo_wallet.filter(promo=promo.id)

            if promo.allowed_per_user and promo.allowed_per_user <= user_promo_dict[promo.id]:
                return self.send_response(0, "Sorry, Invalid Promo Code.")


            if promo.allowed_usage and promo.allowed_usage <= len(current_promo):
                return self.send_response(0, "Sorry, Invalid Promo Code.")

            if promo.allowed_users.all() and not (request.user in promo.allowed_users.all() or request.user.email in promo.allowed_emails):
                return self.send_response(0, "Sorry, Invalid Promo Code.")

           
            #add it to zapwallet
            amount = self.get_promo_amount(promo)
            request.user.issue_zap_wallet(amount, mode='1',purpose='Credited for applying promo code' , promo=promo)  

                # cart.promo = promo
                # cart.save()
                # final_price = cart.cart_price_after_coupon
            return self.send_response(1, {'amount': amount, 'message': 'Promo code is applied.'})

            # else:promo
            #     return self.send_response(0, 'Uh oh! You must shop for at least Rs. {}'.format(promo.min_purchase))
        else:
            return self.send_response(0, 'Sorry! This promo code has expired.')
