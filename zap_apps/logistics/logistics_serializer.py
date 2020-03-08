from zap_apps.logistics.models import LOGISTICS_PARTNERS, Logistics, LogisticsLog
from zap_apps.address.models import Address
from rest_framework import serializers
from zap_apps.order.models import Order


class LogisticsSerializer(serializers.ModelSerializer):
    pickup_partner = serializers.ChoiceField(
        choices=LOGISTICS_PARTNERS, allow_null=True, allow_blank=True, required=False)
    product_delivery_partner = serializers.ChoiceField(
        choices=LOGISTICS_PARTNERS, allow_null=True, allow_blank=True, required=False)
    confirmed_at = serializers.DateTimeField(required=False)
    consignee = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    consignor = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    orders = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), many=True, required=False)

    class Meta:
        model = Logistics
        field = ('orders', 'returns', 'status', 'confirmed_at', 'consignee', 'consignor',
                 'delivery_time', 'triggered_pickup', 'product_delivery_partner', 'pickup_partner', 'zap_inhouse')

    def update(self, instance, validated_data):

        instance.consignor = validated_data.get(
            'consignor', instance.consignor)
        instance.confirmed_at = validated_data.get(
            'confirmed_at', instance.confirmed_at)
        instance.consignee = validated_data.get(
            'consignee', instance.consignee)
        instance.returns = validated_data.get(
            'returns', instance.returns.all())
        instance.orders = validated_data.get('orders', instance.orders.all())
        instance.status = validated_data.get('status', instance.status)
        instance.delivery_time = validated_data.get(
            'delivery_time', instance.delivery_time)
        instance.triggered_pickup = validated_data.get(
            'triggered_pickup', instance.triggered_pickup)
        instance.product_delivery_partner = validated_data.get(
            'product_delivery_partner', instance.product_delivery_partner)
        instance.pickup_partner = validated_data.get(
            'pickup_partner', instance.pickup_partner)
        instance.zap_inhouse = validated_data.get('zap_inhouse', instance.zap_inhouse)
        # instance.zap_inhouse = validated_data.get('zap_inhouse', instance.zap_inhouse)
        instance.save()
        return instance


class LogisticsLogSerializer(serializers.ModelSerializer):
    logistics = serializers.PrimaryKeyRelatedField(
        queryset=Logistics.objects.all(), required=False)
    waybill = serializers.CharField(required=False)
    whole_response = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    extra = serializers.CharField(required=False)
    partner = serializers.ChoiceField(
        choices=LOGISTICS_PARTNERS, required=False)

    class Meta:
        model = LogisticsLog
        field = ('logistics', 'waybill', 'barcode', 'status', 'pickup', 'rejected',
                 'track', 'updated_time', 'whole_response', 'triggered_pickup_at', 'returns', 'partner', 'extra')
