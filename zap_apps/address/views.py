from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from zap_apps.account.zapauth import ZapView, ZapAuthView, zap_login_required
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from zap_apps.zapuser.models import ZapUser, LoggedFrom
from zap_apps.address.models import State, Address, CityPincode
# from zap_apps.account.account_serializer import (FbUserSlzr, InstagramUserSlzr, AccestokenSerializar,
#     AccestokenSerializar, ZapLoginUserSlzr, ZapSignupUserSlzr)
from zap_apps.address.address_serializer import AddressSerializer, GetAddressSerializer, CityPincodeSerializer
import re
# Create your views here.


from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class GetStates(ZapAuthView):

    def get(self, request, format=None):
        return self.send_response(1, State.objects.order_by('name').values('name', 'id'))


class AddressCRUD(ZapAuthView):

    def get(self, request, format=None):
        relation_fields = ['state__name', 'state__id']
        filter_query = {'user': request.user}
        if request.GET.get('address_id'):
            filter_query['id'] = re.search('\d*',request.GET['address_id']).group()

        # states = Address.objects.select_related(*relation_fields).filter(**filter_query).values(*relation_fields)
        addrss = Address.objects.select_related(
            *relation_fields).filter(**filter_query)
        srlzr = GetAddressSerializer(addrss, many=True)
        return Response({'status': 'success', 'data': srlzr.data})

    def post(self, request, format=None):
        data = request.data.copy()
        print data
        data['user'] = request.user.id
        srlzr = AddressSerializer(data=data)
        if srlzr.is_valid():
            s = srlzr.save()
            srlzr = GetAddressSerializer(Address.objects.get(id=s.id))
            return Response({'status': 'success', 'data': srlzr.data})
        return Response({'status': 'error', 'detail': srlzr.errors})

    def put(self, request, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        if not data.get('address_id'):
            return self.send_response(0, "address_id field is required.")
        try:
            address = Address.objects.get(id=data['address_id'], user=request.user)
        except Address.DoesNotExist:
            return self.send_response(0, "Address does not exists.")
        srlzr = AddressSerializer(address, data=data)
        if srlzr.is_valid():
            s = srlzr.save()
            return self.send_response(1, GetAddressSerializer(Address.objects.get(id=s.id)).data)
        return self.send_response(0, srlzr.errors)

    def delete(self, request, format=None):
        data = request.GET.copy()
        Address.objects.filter(
            id=data['address_id'], user=request.user).delete()
        return self.send_response(1, "Address successfully deleted")
from zap_apps.logistics.models import DelhiveryPincode


class Pincode(ZapView):

    def get(self, request, pin, format=None):
        try:
            DelhiveryPincode.objects.get(pincode=pin)
        except DelhiveryPincode.DoesNotExist:
            return self.send_response(0, "This pincode does not available with ZAPYLE.")
        return self.send_response(1, 'success')

class GetCity(ZapView):
    def get(self,request,format=None):
        # import pdb; pdb.set_trace()
        pincode_dict = request.GET.copy()
        pincode = pincode_dict.get('pincode')
        if not isinstance(pincode, str):
            pincode = str(pincode)
        try:
            obj = CityPincode.objects.filter(pincode=pincode)
            if not obj:
                return self.send_response(0,'Pincode not Available')    
            city_data = obj[0]
            srlzr = CityPincodeSerializer(city_data)
            return self.send_response(1, srlzr.data)
        except CityPincode.DoesNotExist:
            return self.send_response(0,'Pincode not Available')





