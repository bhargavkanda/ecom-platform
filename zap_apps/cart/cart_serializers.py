from rest_framework import serializers
from zap_apps.cart.models import Cart, Item
from zap_apps.zap_catalogue.models import NumberOfProducts
from django.conf import settings
from zap_apps.address.address_serializer import GetAddressSerializer

class CartGetSerializer(serializers.Serializer):
    items = serializers.ListField()


class ItemSerializer(serializers.ModelSerializer):

    # def validate_product(self, data):
    #     if not NumberOfProducts.objects.filter(product=data):
    #         return serializers.ValidationError("Oops! This item is sold out.")
    #     return data

    class Meta:
        model = Item
        fields = ('cart', 'product', 'size', 'quantity', 'offer')


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ('success', 'delivery_address')

from zap_apps.payment.models import ZapWallet
from django.db.models import Sum, F

class CheckoutSrlzr(serializers.ModelSerializer):
    zap_cash = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    cod = serializers.SerializerMethodField()
    cod_message = serializers.SerializerMethodField()
    online_message = serializers.SerializerMethodField()
    def get_addresses(self, foo):
        return GetAddressSerializer(foo.user.address_set.all(), many=True).data
    def get_zap_cash(self, foo):
        promo_allowed = 0
        credit_return = foo.user.zapcash_user1.filter(mode=2,credit=True).aggregate(s=Sum(F('amount')))['s'] or 0
        debit_total = foo.user.zapcash_user1.filter(credit=False).aggregate(s=Sum(F('amount')))['s'] or 0
        promo_expense = credit_return - debit_total
        max_promo = round(0.2 * foo.total_listing_price())
        promo_sum = foo.user.zapcash_user1.filter(credit=True, mode__in=[0,1]).aggregate(s=Sum(F('amount')))['s'] or 0
        if promo_expense > 0:
            promo_allowed = min(max_promo, promo_sum) + promo_expense
        else:
            promo_allowed = min(max_promo, promo_sum+promo_expense)
        return promo_allowed#foo.user.get_zap_wallet
    def get_cod(self, foo):
        return True if foo.total_listing_price() < 30000 else False
    def get_cod_message(self, foo):
        if foo.total_listing_price() < 30000:
            return 'Pay by cash on delivery. Please note that we do not accept old notes.'
        else:
            return 'Cash on delivery is available only on orders worth Rs. 30,000 or less.'
    def get_online_message(self, foo):
        return 'Pay securely online via Netbanking, Credit / Debit Card & Wallets'
    class Meta:
        model = Cart
        fields = ('total_listing_price', 'total_original_price', 'total_discount', 'seller_discount', 'zapyle_discount',
            'total_shipping_charge', 'total_price_with_shipping_charge', 'zap_cash', 'addresses', 'cod', 'cod_message', 'online_message')

class GetCartItemSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_listing_price = serializers.SerializerMethodField()
    total_original_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    total_shipping_charge = serializers.SerializerMethodField()
    total_price_with_shipping_charge = serializers.SerializerMethodField()
    seller_discount = serializers.SerializerMethodField()
    zapyle_discount = serializers.SerializerMethodField()
    cart_id = serializers.SerializerMethodField()
    offer_discount = serializers.SerializerMethodField()
    # def get_size(self, obj):
    #     return obj.get_size_string()
    def get_total_price_with_shipping_charge(self, obj):
        return obj.total_price_with_shipping_charge()
    def get_total_shipping_charge(self, obj):
        return obj.total_shipping_charge()
    def get_total_discount(self, obj):
        return obj.total_discount()
    def get_total_original_price(self, obj):
        return obj.total_original_price()
    def get_total_listing_price(self, obj):
        return obj.total_listing_price()
    def get_zapyle_discount(self, obj):
        return obj.zapyle_discount()
    def get_offer_discount(self, obj):
        return obj.offer_discount()
    def get_seller_discount(self, obj):
        return obj.seller_discount()
    def get_cart_id(self, obj):
        return obj.id
    def get_items(self, obj):
        from zap_apps.offer.models import ZapOffer
        return [{'title': i.product.title,
                'product_id': i.product.id,
                'product_image': i.product.images.all().order_by('id')[0].image.url_500x500,
                'product_style': i.product.style.style_type if i.product.style else None,
                'product_brand': i.product.brand.brand,
                'product_size': i.get_size_string(),
                'product_size_id': i.size.id,
                'product_quantity': i.quantity,
                'shipping_charge': settings.SHIPPING_CHARGE if (i.selling_price * i.quantity) < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0,
                'listing_price': i.selling_price,
                'original_price': i.product.original_price,
                'total_price': i.selling_price * i.quantity,
                'offer_benefit': i.offer.get_benefit(i.product.id) if i.offer else None,
                'offer_code': i.offer.code if i.offer else None,
                'id': i.id,
                'offer_invalid': (not i.offer.is_applicable(i.product.id, self.context['user'])['status'] if 'user' in self.context else not i.offer.is_applicable(i.product.id)['status']) if i.offer else None,
                # 'sold_out': i.sold_out,
                'discount': round((1-(i.selling_price/i.product.original_price))*100, 0),
                'quantity_available': NumberOfProducts.objects.get(size=i.size, product=i.product).quantity,
                } for i in obj.item.all().order_by('-id')]

    class Meta:
        model = Cart
        fields = ('items', 'total_listing_price', 'total_original_price', 'total_discount', 'cart_id', 'seller_discount', 'zapyle_discount',
            'total_shipping_charge', 'total_price_with_shipping_charge', 'offer_discount')


class CartSerializerForTransaction(serializers.ModelSerializer):
    ordered_products = serializers.SerializerMethodField()
    listing_price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    shipping_charge = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    zapwallet_used = serializers.SerializerMethodField()
    def get_zapwallet_used(self, foo):
        return self.context['zapwallet_used']
    def get_status(self, foo):
        return "failed"
    def get_shipping_charge(self, obj):
        return obj.total_shipping_charge()
    def get_original_price(self, obj):
        return obj.total_original_price()
    def get_listing_price(self, obj):
        return obj.total_listing_price()
    def get_ordered_products(self, obj):
        # product = obj.product
        return [{'title': i.product.title,
                'image': i.product.images.all()[0].image.url_500x500,
                'style': i.product.style.style_type if i.product.style else None,
                'brand': i.product.brand.brand,
                'size': i.get_size_string(),
                'quantity': i.quantity,
                'shipping_charge': settings.SHIPPING_CHARGE if i.selling_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0,
                'listing_price': i.product.listing_price,
                'offer':i.offer.id if i.offer else None,
                'original_price': i.product.original_price,
                'total_price': i.product.listing_price * i.quantity,
                'id': i.id,
                'discount': 1-(i.product.listing_price/i.product.original_price),
                } for i in obj.item.all()]

    class Meta:
        model = Cart
        field = '__all__'
        exclude = ('user', 'delivery_address')
