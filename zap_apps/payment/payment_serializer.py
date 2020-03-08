from rest_framework import serializers
from zap_apps.zapuser.models import ZapUser, UserPreference
from zap_apps.payment.models import PaymentResponse
from zap_apps.zap_catalogue.models import ApprovedProduct
from rest_framework.validators import UniqueValidator
from zap_apps.payment.models import BillGeneratorModel, Payout, RefundResponse
from zap_apps.order.models import Order, OrderedProduct,  Transaction, Return
from datetime import timedelta
from django.utils import timezone


class RecursiveField(serializers.Serializer):

    def to_native(self, value):
        return self.parent.to_native(value)


class BillGeneratorDataSrlzr(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_size = serializers.IntegerField()
    product_quantity = serializers.IntegerField()


class BillGeneratorModelSrlzr(serializers.ModelSerializer):

    class Meta:
        model = BillGeneratorModel
        fields = ('merchant_transaction_id', 'amount', 'request_signature')


class BillGeneratorSrlzr(serializers.Serializer):
    address_id = serializers.IntegerField()
    data_to_order = serializers.ListField()
    coupon = serializers.CharField(required=False)

    def validate_data_to_order(self, data):
        s = BillGeneratorDataSrlzr(data=data, many=True)
        if not s.is_valid():
            raise serializers.ValidationError(s.errors)
        return data


class PaymentResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentResponse

        field = '__all__'


class PayoutSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=False)
    seller = serializers.PrimaryKeyRelatedField(
        queryset=ZapUser.objects.all(), required=False)

    class Meta:
        model = Payout
        field = ('seller', 'order', 'payout_status ', 'error_message', 'total_value', 'seller_cut', 'zapyle_cut')

        def update(self, instance, validated_data):
            # instance.cancelled = validated_data.get('cancelled', instance.cancelled)
            instance.error_message = validated_data.get(
                'error_message', instance.error_message)
            instance.payout_status = validated_data.get(
                'payout_status', instance.payout_status)

            instance.save()
            return instance
class OrderedPrdctSrlzr(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    def get_image(self, foo):
        return foo.image.image.url_500x500 if foo.image else ""
    quantity = serializers.SerializerMethodField()
    
    def get_quantity(self, foo):
        return foo.quantity
    class Meta:
        model = OrderedProduct
        field = '__all__'

class TransSrlzr(serializers.ModelSerializer):
    ordered_products = serializers.SerializerMethodField()
    def get_ordered_products(self, foo):
        return OrderedPrdctSrlzr(foo.ordered_products(), many=True).data
    class Meta:
        model = Transaction
        fields = ('status', 'listing_price', 'original_price', 'shipping_charge', 'zapwallet_used','ordered_products')

class SingleTransactionSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField('get_seller_details')
    products = serializers.SerializerMethodField('get_all_cart_items')
    shipping_charge = serializers.SerializerMethodField('get_shipping_charges')
    quantity = serializers.SerializerMethodField('get_quantities')
    coupon = serializers.SerializerMethodField()
    coupon_name = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    address_id = serializers.SerializerMethodField()
    zapcash_used = serializers.SerializerMethodField()

    def get_zapcash_used(self, obj):
        return obj.zapwallet_used
        
    def get_address_id(self, obj):
        return obj.cart.delivery_address.id
    def get_size(self, obj):
        s = obj.cart.items.all()[0].size.uk_size
        return 'FREESIZE' if s == '0' else 'UK'+s  
    def get_coupon(self,obj):
        return obj.cart.get_coupon_discount if obj.cart.coupon else 0
    def get_coupon_name(self,obj):
        return obj.cart.coupon.coupon_code if obj.cart.coupon else ''
        

    def get_seller_details(self, obj):
        return {'id': obj.cart.items.all()[0].product.user.id, 'name': obj.cart.items.all()[0].product.user.zap_username, 'profile_pic': obj.cart.items.all()[0].product.user.profile.profile_pic,'user_type':obj.cart.items.all()[0].product.user.user_type.name}

    def get_all_cart_items(self, obj):
        return [ProductSerializer(item.product).data for item in obj.cart.items.all()]

    def get_shipping_charges(self, obj):
        return obj.cart.shipping_charge

    def get_quantities(self, obj):
        return obj.cart.items.all()[0].quantity

    class Meta:
        model = Transaction
        fields = ('final_price', 'success', 'transaction_ref', 'zapcash_used', 'products', 'seller','coupon_name',
                  'shipping_charge', 'total_price', 'quantity', 'coupon', 'zapcash_used','size','address_id')

class GetTransactionSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField('get_all_cart_items')
    shipping_charge = serializers.SerializerMethodField('get_shipping_charges')
    listing_price_sum = serializers.SerializerMethodField('get_listing_price')
    quantity = serializers.SerializerMethodField('get_quantities')
    can_return = serializers.SerializerMethodField()
    # order_id = serializers.SerializerMethodField()
    # def get_order_id(self, foo):
    #     return foo.order.all()[0].order.id if foo.success else None

    def get_can_return(self, foo):
        if foo.success:
            order = foo.order.all()[0]
            return False if not order.delivery_date else True if (order.delivery_date + timedelta(hours=24)) > timezone.now() and not Return.objects.filter(order_id=order).exists() else False
        else:
            return False

    def get_all_cart_items(self, obj):
        return [ProductSerializer(item.product).data for item in obj.cart.items.all()]

    def get_shipping_charges(self, obj):
        return obj.cart.shipping_charge

    def get_listing_price(self, obj):
        return obj.listing_price_sum

    def get_quantities(self, obj):
        return obj.cart.items.all()[0].quantity

    class Meta:
        model = Transaction
        fields = ('can_return', 'success', 'transaction_ref', 'products',
                  'shipping_charge', 'listing_price_sum', 'quantity')


class ProductSerializer(serializers.ModelSerializer):
    image1 = serializers.SerializerMethodField('get_first_image')
    style = serializers.SerializerMethodField('get_styles')
    brand = serializers.SerializerMethodField('get_brands')

    def get_styles(self, obj):
        return obj.style.style_type if obj.style else None

    def get_brands(self, obj):
        return obj.brand.brand

    def get_first_image(self, obj):
        return obj.images.all()[0].image.url_500x500

    class Meta:
        model = ApprovedProduct
        fields = ('id', 'title', 'image1', 'style', 'brand',
                  'original_price', 'listing_price', 'discount')

class RefundResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundResponse
        fields = '__all__'


