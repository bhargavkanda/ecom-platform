from rest_framework import serializers
from zap_apps.address.models import Address, CityPincode
from zap_apps.logistics.models import DelhiveryPincode
import re
from zap_apps.zap_commons.common_serializers import ZapErrorModelSrlzr


def check_phone_number(num):
    return bool(re.match(r'^(\+91|0091|0[\-\s]?)?\d{10}$', str(num)))


class AddressSerializer(ZapErrorModelSrlzr):

    def validate_phone(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Mobile number is not valid.")
        return data

    def validate_pincode(self, data):
        try:
            DelhiveryPincode.objects.get(pincode=data)
        except DelhiveryPincode.DoesNotExist:
            raise serializers.ValidationError(
                "This pincode is not available with ZAPYLE.")
        return data

    class Meta:
        model = Address
        fields = ('id', 'user', 'name', 'address', 'address2',
                  'city', 'state', 'phone', 'pincode')


class GetAddressSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source='state.name', read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'name', 'address', 'address2',
                  'city', 'state', 'phone', 'pincode')



class CityPincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityPincode
        fields = '__all__'