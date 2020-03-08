# -*- coding: utf-8 -*-

from rest_framework import serializers
from zap_apps.order.models import Order, Transaction, RETURN_REASONS, Return
from zap_apps.address.models import Address
from zap_apps.address.address_serializer import GetAddressSerializer
from rest_framework.validators import UniqueValidator
from zap_apps.zap_catalogue.models import ApprovedProduct, Size
from zap_apps.offer.models import ZapOffer
from django.utils import timezone
import datetime as dt


# class OrderSerializer(serializers.ModelSerializer):
#     consignor = serializers.PrimaryKeyRelatedField(
#         required=False, queryset=Address.objects.all())
#     class Meta:
#         model = Order
#         fields = ('transaction', 'order_number', 'product', 'quantity',
#                   'consignee', 'consignor', 'total_price', 'confirmed', 'size')


class TransactionSerializer(serializers.ModelSerializer):
    from zap_apps.cart.models import Cart
    from zap_apps.zapuser.models import ZapUser


    class Meta:
        model = Transaction
        field = '__all__'

    # def update(self, instance, validated_data):
    #     instance.paid_out = validated_data.get('paid_out', instance.paid_out)
    #     instance.initiate_payout = validated_data.get('initiate_payout', instance.initiate_payout)
    #     instance.cod = validated_data.get('cod', instance.cod)
    #     instance.save()
    #     return instance


class OrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=ApprovedProduct.ap_objects.all(), required=False)
    transaction = serializers.PrimaryKeyRelatedField(
        queryset=Transaction.objects.all(), required=False)
    consignee = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    consignor = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    size = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), required=False)
    delivery_date = serializers.DateTimeField(required=False)
    initiate_payout = serializers.BooleanField(required=False)
    total_price = serializers.CharField(required=False)
    order_number = serializers.CharField(required=False)
    final_price = serializers.FloatField(required=False)
    offer = serializers.PrimaryKeyRelatedField(queryset=ZapOffer.objects.all(), required=False)

    class Meta:
        model = Order
        field = ('transaction', 'product', 'cancelled', 'returned', 'consignee',
                 'consignor', 'quantity', 'triggered_logistics', 'delivery_date', 'offer')

    def update(self, instance, validated_data):
        # instance.cancelled = validated_data.get(
        #     'cancelled', instance.cancelled)
        # instance.returned = validated_data.get('returned', instance.returned)
        instance.delivery_date = validated_data.get(
            'delivery_date', instance.delivery_date)
        instance.triggered_logistics = validated_data.get(
            'triggered_logistics', instance.triggered_logistics)

        instance.product = validated_data.get('product', instance.product)
        instance.transaction = validated_data.get(
            'transaction', instance.transaction)
        instance.consignee = validated_data.get(
            'consignee', instance.consignee)
        instance.consignor = validated_data.get(
            'consignor', instance.consignor)
        instance.size = validated_data.get('size', instance.size)
        # instance.order_number = validated_data.get('order_number', instance.order_number)
        # instance.total_price = validated_data.get('total_price',instance.total_price)

        # instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance


class ReturnSerializer(serializers.ModelSerializer):
    reason = serializers.ChoiceField(
        choices=RETURN_REASONS, allow_null=True, allow_blank=True, required=False)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=False)

    consignee = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    consignor = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    value = serializers.FloatField(required=False)
    # delivery_date = serializers.DateTimeField(required=False)
    # initiate_payout = serializers.BooleanField(required=False)

    class Meta:
        model = Return
        field = ('order_id', 'reason', 'consignee', 'consignor', 'requested_at', 'delivery_date',
                 'approved', 'value', 'credited', 'self_return', 'triggered_logistics', 'approved_zapcash')

    def update(self, instance, validated_data):

        instance.requested_at = validated_data.get(
            'requested_at', instance.requested_at)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.delivery_date = validated_data.get(
            'delivery_date', instance.delivery_date)
        instance.triggered_logistics = validated_data.get(
            'triggered_logistics', instance.triggered_logistics)
        instance.approved = validated_data.get('approved', instance.approved)
        instance.credited = validated_data.get('credited', instance.credited)
        instance.self_return = validated_data.get(
            'self_return', instance.self_return)
        instance.save()
        return instance

class SingleOrderSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    delivery_address = serializers.SerializerMethodField()
    # order_status = serializers.SerializerMethodField()
    amount_paid = serializers.SerializerMethodField()
    payout_mode = serializers.SerializerMethodField()
    tracker = serializers.SerializerMethodField()
    placed_at = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    offer = serializers.SerializerMethodField()
    # current_status = serializers.SerializerMethodField()
    def get_payout_mode(self, foo):
        return foo.transaction.get_payment_mode_display()
    def get_amount_paid(self, foo):
        return foo.final_price
    def get_product(self, foo):
        return {'title':foo.product.title,'id':foo.product.id}
    def get_seller(self, foo):
        return foo.consignor.user.zap_username
    def get_size(self, foo):
        return foo.ordered_product.size.replace('_','-')
    def get_delivery_address(self, foo):
        return GetAddressSerializer(foo.transaction.consignee).data
    def get_rating(self, foo):
        if foo.delivery_date == None:
            return False
        else:
            if foo.rating == None or foo.rating == '':
                return '0'
            else:
                return str(foo.rating)

    def get_offer(self, foo):
        if foo.offer:
            return {'name': foo.offer.name, 'benefit': int(foo.product.listing_price - foo.product.get_offer_price(foo.offer.id)) }

    # def get_current_status(self, foo):
    #     if foo.order_status == 'confirmed':
    #         return {'status' : 'confirmΩed', 'step' : 1}
    #     elif foo.order_status == 'picked_up':
    #         return {'status' : 'picked_up', 'step' : 2}
    #     elif foo.order_status in ['verification','cancelled','product_rejected','on_hold']:
    #         return {'status': foo.order_status, 'step' : 3}
    #     elif foo.order_status == 'on_the_way_to_you':
    #         return {'status' : 'on_the_way_to_you', 'step' : 4}
    #     elif foo.order_status in ['delivered','return_requested','return_in_process','returned']:
    #         return {'status' : foo.order_status, 'step' : 5}
    #     else:
    #         return {'status' : foo.order_status, 'step' : 0}
    def get_tracker(self, o):
        current_status = o.order_status
        description = ''
        current_title = ''
        tracker = []
        cta = False
        try:
            print o.order_status
            print o.product.time_to_make,'time_to_make'
            INCLUDE_MAKING = True if o.product.time_to_make else False
            ALL_COMPLETED_STATUSES = ['confirmed']+['made']*INCLUDE_MAKING+['picked_up','product_approved','on_the_way_to_you','delivered', 'return_requested', 'return_in_process', 'returned']
            if current_status in ['being_confirmed','pending']:
                step = 1
                description = ORDER_DESCRIPTIONS[current_status]
                current_title = DEFAULT_RESPONSE[0]['title']
                tracker = [DEFAULT_RESPONSE[0]]+[DEFAULT_RESPONSE[5]]*INCLUDE_MAKING+[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status == 'failed':
                step = 1
                tracker = [{'status':'Order Failed','title':'Order Failed'}]
                description = ORDER_DESCRIPTIONS['failed']
                current_title = o.get_order_status_display()
            elif current_status == 'confirmed':
                step = 1
                description = ORDER_DESCRIPTIONS['confirmed']
                current_title = o.get_order_status_display()
                tracker = [{'time':o.track_order.get(status='confirmed').time,'status':'confirmed'}]\
                +[DEFAULT_RESPONSE[5]]*INCLUDE_MAKING+[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status == 'being_made':
                step = 2
                description = ORDER_DESCRIPTIONS['being_made'].format(o.product.time_to_make)
                current_title = o.get_order_status_display()
                tracker = [{'time':o.track_order.get(status='confirmed').time,'status':'confirmed'}]\
                +[DEFAULT_RESPONSE[5]]*INCLUDE_MAKING+[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status == 'made':
                step = 2
                description = ORDER_DESCRIPTIONS['made']
                current_title = o.get_order_status_display()
                tracker = [{'time':o.track_order.get(status='confirmed').time,'status':'confirmed'}]\
                +[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status == 'pickup_in_process':
                step = 2 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['pickup_in_process']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[1]]+[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status == 'picked_up':
                step = 2 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['picked_up']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[2]]+[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status == 'verification':
                step = 3 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['verification']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]                
            elif current_status == 'product_approved':
                step = 3 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['product_approved']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[3]]+[DEFAULT_RESPONSE[4]]
            elif current_status in ['on_the_way_to_you','on_hold']:
                step = 4 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS[current_status]
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[4]]
            elif current_status == 'delivered':
                step = 5 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['delivered']
                current_title = o.get_order_status_display()
                print o.track_order.get(status='delivered').id
                f = timezone.now() - o.track_order.get(status='delivered').time
                print f.total_seconds()//3600 ,'hoy'
                if (f.total_seconds()//3600) <= 24:
                    cta = True
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]
            elif current_status == 'cancelled':
                description = ORDER_DESCRIPTIONS['cancelled']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=['confirmed','picked_up','product_approved','on_the_way_to_you','delivered','cancelled']).order_by('time')]
                step = len(tracker)
            elif current_status == 'return_requested':
                step = 6 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['return_requested']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[6]]+[DEFAULT_RESPONSE[7]]
            elif current_status == 'return_in_process':
                step = 7 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['return_in_process']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]\
                +[DEFAULT_RESPONSE[7]]
            elif current_status == 'returned':
                step = 8 + 1*INCLUDE_MAKING
                description = ORDER_DESCRIPTIONS['returned']
                current_title = o.get_order_status_display()
                tracker = [{'title':i.get_status_display(),'time':i.time} for i in o.track_order.filter(status__in=ALL_COMPLETED_STATUSES[0:step]).order_by('time')]
        except Exception as e:
            print e.message,'error'
        return {'steps':tracker,'current_step':step-1,'current_title':current_title,'description':description,'cta':cta}
    
    def get_placed_at(self, obj):
        delta = dt.timedelta(hours=5, minutes=30)
        return (obj.placed_at+delta).replace(tzinfo=None).strftime('%d %b, %Y %H:%M %p')
    class Meta:
        model = Order
        fields = ('id','product','quantity','size','order_number','seller','placed_at','zapwallet_used','delivery_address','payout_mode','amount_paid','tracker', 'rating', 'offer')

DEFAULT_RESPONSE = [
    {
        'title':'Order being Confirmed',
    },
    {
        'title':'Product is yet to be picked up from the Seller',
    },
    {
        'title':'Zap Authentication yet to be done',
    },
    {
        'title':'Order yet to be Shipped',
    },
    {
        'title':'Order yet to be delivered.',
    },
    {
        'title':'Product is yet to be made',
    },
    {
        'title':'Return to be confirmed',
    },
    {
        'title':'Product yet to be returned',
    }
]
ORDER_DESCRIPTIONS = {
    'pending': 'Order is yet to be confirmed with the payment partner.',
    'failed': 'Order failed with the payment partner.',
    'being_confirmed': 'Order is being confirmed with the buyer and the seller.',
    'cancelled': 'Order is cancelled.',
    'confirmed': 'Order is confirmed.',
    'being_made':'The product is being made. It takes around {}.',
    'made':'The product is made and ready to be picked up',
    'pickup_in_process': 'Product is getting picked up from Seller.',
    'picked_up': 'Product is picked up from Seller.',
    'verification': 'Zapyle is checking for product authenticity. Typically takes 1-2 working days.',
    'product_approved': 'Product is approved by Zapyle.',
    'product_rejected': 'Product is rejected since it failed to meet the authenticity standards.',
    'on_the_way_to_you': 'The product is shipped and is on its way.',
    'delivered': 'Order is delivered to buyer',
    'return_requested': 'Return Requested for Approval',
    'on_hold': 'The courier partner has made multiple failed delivery attempts. Please contact team@zapyle.com for more details.',
    'return_in_process':'Your return request has been approved and is being processed',
    'returned':'Your return is completed.'
}