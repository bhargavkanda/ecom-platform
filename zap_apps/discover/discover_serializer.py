from rest_framework import serializers
from zap_apps.discover.models import (ACTION_TYPES, Homefeed, ZapAction, Banner, Message,
                                      ProductCollection, UserCollection, Closet, CustomCollection, Generic, CTA)
import pdb
from collections import OrderedDict
from django.conf import settings

class ZapActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZapAction
        field = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    image_resolution = serializers.SerializerMethodField()


    def get_image(self,foo):
        if foo.image_web or foo.image:
            if (not self.context.get('platform') and foo.image) or (
                    self.context.get('mobile_website') == 'true' and foo.image):
                return settings.CURRENT_DOMAIN + foo.image.url
            elif foo.image_web:
                return settings.CURRENT_DOMAIN + foo.image_web.url
            else:
                return None
        else:
            return None

    def get_action(self, foo):
        return ZapActionSerializer(foo.action).data
    def get_image_resolution(self, foo):
        return {'width': foo.image_width, 'height': foo.image_height}

    class Meta:
        model = Banner
        fields = ('title', 'description', 'image', 'action', 'image_resolution')


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        field = "__all__"


class ProductCollectionSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    header_image = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    def get_header_image(self, foo):
        if str(foo.header_image) == '' or str(foo.header_image) == None:
            return None
        else:
            return '/zapmedia/'+str(foo.header_image)

    def get_product(self, foo):
        platform = self.context.get('platform')
        return [{'id': t.id, 'image': settings.CURRENT_DOMAIN + t.images.all().order_by('id')[0].image.url_500x500,
                 'title': t.title, 'brand': t.brand.brand, 'original_price': t.original_price,
                 'listing_price': t.listing_price, 'product_type': 'PRE OWNED' if t.shop in [2, 3] else 'BRAND NEW'} for t in foo.product(manager='ap_objects').all()[0:6]]

    def get_target(self, foo):
        return '?i_product_collection=' + str(foo.id)

    class Meta:
        model = ProductCollection
        fields = ('id', 'title', 'description', 'cta_text', 'product', 'header_image', 'target')


class UserCollectionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, foo):
        current_user_id = self.context['current_user_id']
        return [{'id': u.id, 'profile_image': u.profile.profile_pic, 'full_name': u.get_full_name(), 
        'zap_username': u.zap_username, 'cta': CTASerializer(foo.cta).data, 
        'admirers': u.profile.admiring.all().count(), 'outfits': u.get_approved_products().count(),
        'admiring': current_user_id in u.profile.admiring.all().values_list('id', flat=True)} for u in foo.user.all()]

    class Meta:
        model = UserCollection
        field = ('user')


class CTASerializer(serializers.ModelSerializer):

    class Meta:
        model = CTA
        field = "__all__"


class ClosetSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    cta = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    image_resolution = serializers.SerializerMethodField()

    def get_user(self, foo):
        current_user_id = self.context['current_user_id']
        return {'id':foo.user.id, 'zap_username':foo.user.zap_username, 'full_name': foo.user.get_full_name(), 'admiring': current_user_id in foo.user.profile.admiring.all().values_list('id', flat=True)}

    def get_product(self, foo):
        return [{'id': i.id, 'title':i.title, 'brand':i.brand.brand, 'original_price': i.original_price, 'listing_price': i.listing_price, 'image': settings.CURRENT_DOMAIN + i.images.all().order_by('id')[0].image.url_500x500} for i in foo.product.all()]

    def get_cta(self, foo):
        return CTASerializer(foo.cta).data

    def get_image(self, foo):
        return settings.CURRENT_DOMAIN + foo.image.url if foo.image else foo.user.profile.profile_pic
    def get_image_resolution(self, foo):
        return {'width': foo.image_width, 'height': foo.image_height}

    class Meta:
        model = Closet
        fields = ('title', 'user', 'product', 'description', 'cta', 'image', 'image_resolution')


class CustomCollectionSerializer(serializers.ModelSerializer):
    collection = serializers.SerializerMethodField()

    def get_collection(self, foo):
        return BannerSerializer(foo.collection.all().order_by('title'), many=True).data

    class Meta:
        model = CustomCollection
        fields = ('title', 'description', 'collection', 'number_in_row')


class GenericSerialzier(serializers.ModelSerializer):
    cta = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    image_resolution = serializers.SerializerMethodField()

    def get_action(self, foo):
        return ZapActionSerializer(foo.action).data

    def get_cta(self, foo):
        return CTASerializer(foo.cta).data
    def get_image(self, foo):
        return settings.CURRENT_DOMAIN + foo.image.url
    def get_image_resolution(self, foo):
        return {'width': foo.image_width, 'height': foo.image_height}

    class Meta:
        model = Generic
        fields = ('title', 'image', 'description', 'cta', 'action', 'image_resolution')
    


class HomefeedSerializer(serializers.ModelSerializer):
    
    #  = serializers.SerializerMethodField()
    content_data = serializers.SerializerMethodField()

    def get_content_data(self, foo):
        # pdb.set_trace()
        current_user_id = self.context['current_user_id']
        platform = self.context.get('platform')
        mobile_website = self.context.get('mobile_website')
        if foo.banner:
            return {'discover_type':'banner', 'discover_data': BannerSerializer(foo.banner, context={'platform': platform, 'mobile_website':mobile_website}).data}
        elif foo.message:
            return {'discover_type':'message', 'discover_data':MessageSerializer(foo.message).data}
        elif foo.product_collection:
            return {'discover_type': 'product_collection',
                    'discover_data': ProductCollectionSerializer(foo.product_collection, context={'platform': platform}).data}
        elif foo.user_collection:
            return {'discover_type':'user_collection', 'discover_data':UserCollectionSerializer(foo.user_collection, context={'current_user_id': current_user_id}).data}
        elif foo.closet:
            return {'discover_type':'closet', 'discover_data':ClosetSerializer(foo.closet, context={'current_user_id': current_user_id}).data}
        elif foo.custom_collection:
            return {'discover_type':'custom_collection', 'discover_data':CustomCollectionSerializer(foo.custom_collection).data}
        else:
            return {'discover_type':'generic', 'discover_data':GenericSerialzier(foo.generic).data}

    

    class Meta:
        model = Homefeed
        # fields = ('banner', 'message', 'product_collection',
        #           'user_collection', 'closet', 'custom_collection', 'generic')
        field = ('content_data')

    def to_representation(self, instance):
            ret = super(HomefeedSerializer, self).to_representation(instance)
            # Here we filter the null values and creates a new dictionary
            # We use OrderedDict like in original method
            ret = OrderedDict(list(filter(lambda x: x[1], ret.items())))
            return ret
