from django.shortcuts import render
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from zap_apps.zap_catalogue.helpers import checkAvailability
from zap_apps.cart.models import Item, Cart
# from zap_apps.account.zapauth import ZapView, ZapAuthView
from zap_apps.zap_catalogue.models import Size, NumberOfProducts, ApprovedProduct
from zap_apps.cart.cart_serializers import ItemSerializer, CartSerializer, CartGetSerializer, GetCartItemSerializer, CheckoutSrlzr
from zap_apps.offer.models import ZapOffer
# Create your views here.
from django.conf import settings



class Checkout(ZapAuthView):
    def get(self, request, format=None):
        cart = request.user.cart
        srlzr = CheckoutSrlzr(cart)
        return self.send_response(1, srlzr.data)

class ZapCart(ZapAuthView):

    def post(self, request, format=None):
        post_data = request.data.copy()
        if not post_data.get('cart_data') or not isinstance(post_data.get('cart_data'), (list, dict)):
            return self.send_response(0, "Please send items in cart_data")
        if isinstance(post_data.get('cart_data'), dict):
            datas = [post_data['cart_data']]
        else:
            datas = post_data['cart_data']
        if 'from' in post_data:
            for i in request.user.cart.item.all():
                i.delete()
        for data in datas:
            try:
                product = ApprovedProduct.ap_objects.get(id=data['product'])
            except Exception:
                self.send_response(0, 'Product does not exist')
            web_message = product.brand.brand + " " + product.title + " added successfully."
            data['cart'] = request.user.cart.id
            if 'offer' in data:
                try:
                    offer = ZapOffer.objects.get(id=data['offer'])
                    if request.user.is_authenticated():
                        applicable = offer.is_applicable(data['product'], request.user.id)
                    else:
                        applicable = offer.is_applicable(data['product'])
                    if applicable['status']:
                        data.update({'offer': offer.id})
                    else:
                        web_message = web_message + ' ' + applicable['error']
                except Exception:
                    web_message = web_message + ' Sorry! The offer is not valid.'
            # else:
            #     offers_available = ApprovedProduct.objects.get(id=data['product']).get_offers(type='SITE', when='ADD_CART')
            #     if len(offers_available) > 0:
            #         data.update({'offer':offers_available[0].id})
            if not 'size' in data or not data['size'] or data['size'] == 'FREESIZE':  # check for freesize
                data['size'] = Size.objects.get(category_type="FS").id
            srlzr = ItemSerializer(data=data)
            if not srlzr.is_valid():
                return self.send_response(0, srlzr.errors)
            if checkAvailability(data['product'], data['size'], int(data.get('quantity', 1))):
                if request.user.cart.item.filter(size=data['size'], product=data['product']):
                    if request.user.cart.item.filter(size=data['size'], product=data['product'])[0].quantity == int(data.get('quantity', 1)):
                        web_message = product.brand.brand + " " + product.title + " is already added to your tote."
                    request.user.cart.item.filter(size=data['size'], product=data['product']).update(quantity=int(data.get('quantity', 1)))
                    continue
                s = srlzr.save()
            else:
                if isinstance(post_data['cart_data'], dict):
                    return self.send_response(0, "Sorry, this item is just sold out!.")
        # cart = request.user.cart
        # self.reload(cart)
        # srlzr = GetCartItemSerializer(cart)
        if not request.GET.get('web',False):
            return self.send_response(1, "Item added successfully.")
        else:
            return self.send_response(1, {'message':web_message,'count':request.user.cart.item.count()})
    # REMOVE ITEM FROM CART OR DELETE CART
    def delete(self, request, format=None):
        cart = request.user.cart
        data = request.GET.copy()
        # print data,'dataaaaaa'
        if 'item_id' in data:
            try:
                Item.objects.get(id=data['item_id'], cart__user=request.user).delete()
            except Item.DoesNotExist:
                pass
            self.reload(cart)
        else:
            self.reload_with_remove(cart)    
        srlzr = GetCartItemSerializer(request.user.cart)
        # print srlzr.data
        return self.send_response(1, srlzr.data)

    def reload(self, cart):
        for i in cart.item.all():
            if not i.product.status == '1':
                i.delete()
                continue
        if cart.offer:
            applicable = cart.offer.is_applicable(user_id=cart.user.id)
            if not applicable['status']:
                cart.offer = None
                cart.save()
            # p = NumberOfProducts.objects.get(size=i.size, product=i.product)
            # if i.quantity > p.quantity:
            #     i.quantity = p.quantity
            #     i.save()

    def reload_with_remove(self, cart):
        for i in cart.item.all():
            p = NumberOfProducts.objects.get(size=i.size, product=i.product)
            if p.quantity == 0:
                i.delete()

    # CART DETAILS DO GET METHOD
    def get(self, request, format=None):
        cart = request.user.cart
        if request.GET.get('action') == 'count':
            return self.send_response(1, {'count': cart.item.all().count()})
        self.reload(cart)
        if request.user.is_authenticated():
            srlzr = GetCartItemSerializer(cart, context={'user':request.user.id})
        else:
            srlzr = GetCartItemSerializer(cart)
        return self.send_response(1, srlzr.data)

    # def put(self, request, format=None):
    #     data = request.data
    #     print data, 'zap cart put view'
    #     if not 'size' in data:  # check for freesize
    #         data['size'] = Size.objects.get(category_type="FS").id
    #     srlzr = ItemSerializer(data=data)
    #     if not srlzr.is_valid():
    #         print srlzr.errors, ' item serializer invalid'
    #         return self.send_response(0, srlzr.errors)

    #     try:
    #         available_quantity = NumberOfProducts.objects.get(
    #             product_id=int(data['product']), size_id=int(data['size']))
    #         # print available_quantity.quantity
    #         available_quantity = available_quantity.quantity
    #         # print available_quantity.quantity,'availablequantity'
    #     except Exception as e:
    #         print str(e)
    #         print 'item not availabe22ssss'
    #         return self.send_response(0, "item not availabe")
    #     if data['quantity'] > available_quantity:
    #         return self.send_response(0, {'available': available_quantity, 'ordered_quantity': data['quantity']})

    #     cart, c = Cart.objects.get_or_create(user=request.user, success=False)
    #     s = srlzr.save()
    #     cart.items.all().delete()
    #     cart.coupon = None
    #     cart.items.add(s)
    #     cart.add_shipping_charge_to_cart()
    #     cart.save()
    #     srlzr = GetCartItemSerializer(cart)
    #     print srlzr.data, ' cart data in put'
    #     return self.send_response(1, srlzr.data)


class AddToCart(ZapAuthView):

    def post(self, request, format=None):
        data = request.data
        srlzr = ItemSerializer(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        s, d = Item.objects.get_or_create(product_id=data['product'], quantity=data[
                                          'quantity'], size_id=data['size'])

        cart, c = Cart.objects.get_or_create(
            user=request.user,
            success=False
        )
        if s in cart.items.all():
            return self.send_response(1, 'item already added')
        else:
            cart.items.add(s)

        return self.send_response(1, "item added to cart successfully.")

    def get(self, request, format=None):
        return self.send_response(1, 'item already added')

class ProductAvailability(ZapView):
    def post(self, request, format=None):
        data = request.data
        total_listing_price = 0
        for d in data:
            d['quantity_available'] = NumberOfProducts.objects.get(product=d['product'],size=d['size']).quantity
            if 'offer' in d:
                try:
                    offer = ZapOffer.objects.get(id=d['offer'])
                    d['offer_code'] = offer.code
                    if not offer.is_applicable(d['product']):
                        d['offer_invalid'] = True
                        d['listing_price'] = ApprovedProduct.objects.get(id=d['product']).listing_price
                except Exception:
                    d['offer_invalid'] = True
                    d['listing_price'] = ApprovedProduct.objects.get(id=d['product']).listing_price
            total_listing_price += int(d['listing_price'])
        return self.send_response(1, {'total_listing_price':total_listing_price,'items':data})

class AddtoCartGuest(ZapView):

    def post(self, request, format=None):
        data = request.data.copy()
        product_data = {}
        if checkAvailability(data['product'], data['size'], int(data.get('quantity', 1))):
            product = ApprovedProduct.objects.get(id=data['product'])
            product_data.update({'product':data['product'], 'product_size':data['size'], 'product_quantity':data['quantity'],
                                 'title':product.get_title(), 'listing_price':product.listing_price,
                                 'original_price':product.original_price, 'product_brand':product.brand.brand,
                                 'quantity_available': product.product_count.filter(size=data['size'])[0].quantity,
                                 'product_image': product.images.all().order_by('id')[0].image.url_1000x1000})
            if 'offer' in data:
                if unicode(data['offer']).isdigit():
                    offer = ZapOffer.objects.get(id=data['offer'])
                else:
                    offer = ZapOffer.objects.get(code=data['offer'])
                if not offer.offer_available_on_product(data['product']):
                    return self.send_response(0, "Offer " + offer.name + " cannot be applied on " + data['product'])
                else:
                    product_data.update({'offer': {}})
                    product_data['offer'].update({'id':offer.id, 'code': offer.code, 'name': offer.name,
                                                  'description': offer.description,
                                                  'offer_price': product.get_offer_price(offer.id)})
            # else:
            #     offers_available = ApprovedProduct.objects.get(id=data['product']).get_offers(type='SITE', when='ADD_CART')
            #     if len(offers_available) > 0:
            #         product_data.update({'offer': {}})
            #         offer = offers_available[0]
            #         product_data['offer'].update({'id': offer.id, 'code': offer.code, 'name': offer.name,
            #                                       'description': offer.description,
            #                                       'offer_price': product.get_offer_price(offer.id)})
            return self.send_response(1, product_data)
        else:
            return self.send_response(0, "Sorry, item is just sold out!.")
