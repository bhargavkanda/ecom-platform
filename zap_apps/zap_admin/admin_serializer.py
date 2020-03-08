from zap_apps.zap_catalogue.models import ApprovedProduct
from zap_apps.zapuser.models import ZapUser, ZapExclusiveUserData, UserProfile
from zap_apps.order.models import Order, Return
from zap_apps.marketing.models import Notifs, Action
from zap_apps.zap_catalogue.product_serializer import AndroidUserSerializer
from rest_framework import serializers
from zap_apps.logistics.models import Logistics, LogisticsLog, LOGISTICS_PARTNERS, LOGISTICS_STATUS
from zap_apps.address.models import Address
from django.utils import timesince, timezone
from django.conf import settings
from zap_apps.account.account_serializer import check_phone_number
from zap_apps.zap_admin.models import ADMIN_STATUS
from collections import OrderedDict
from django.db.models import Sum
import pdb


class LandingPageSrlzr(serializers.Serializer):

    email = serializers.EmailField(max_length=50, error_messages=settings.ZAPERROR.error_messages.email.__dict__)
    name = serializers.CharField(max_length=30, error_messages=settings.ZAPERROR.error_messages.name.__dict__)
    phone_number = serializers.CharField(min_length=10, max_length=14, error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)


    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Invalid phone number.")
        return data

class LandingPageSrlzr2(serializers.Serializer):
    name = serializers.CharField(max_length=30, error_messages=settings.ZAPERROR.error_messages.name.__dict__)
    phone_number = serializers.CharField(min_length=10, max_length=14, error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)


    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Invalid phone number.")
        return data


class LandingPageSrlzr(serializers.Serializer):

    email = serializers.EmailField(max_length=30, error_messages=settings.ZAPERROR.error_messages.email.__dict__)
    name = serializers.CharField(max_length=30, error_messages=settings.ZAPERROR.error_messages.name.__dict__)
    phone_number = serializers.CharField(min_length=10, max_length=14, error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)


    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Invalid phone number.")
        return data

class LandingPageSrlzr2(serializers.Serializer):
    name = serializers.CharField(max_length=30, error_messages=settings.ZAPERROR.error_messages.name.__dict__)
    phone_number = serializers.CharField(min_length=10, max_length=14, error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)


    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Invalid phone number.")
        return data

class ApprovedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedProduct
        fields = ('user', 'title', 'pickup_address', 'images', 'description', 'style', 'brand', 'original_price', 'upload_time', 'sale','status','disapproved_reason',
                  'listing_price', 'occasion', 'product_category', 'color', 'completed', 'age', 'condition', 'discount', 'size', 'size_type','time_to_make','percentage_commission')

class ApprovedProductsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user_details')
    no_of_products = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    thumbnails = serializers.SerializerMethodField()
    parcel = serializers.SerializerMethodField()
    send_pushnot = serializers.SerializerMethodField()
    def get_send_pushnot(self, foo):
        return True
    def get_user_details(self, foo):
        return {'id': foo.user.id, 'num_of_products': foo.user.approved_product(manager='ap_objects').count(), 'profile_pic': foo.user.profile.profile_pic, 'zap_username': foo.user.zap_username}
    def get_no_of_products(self, foo):
        size_type = foo.size_type
        return [{'qty': c.quantity, 'size': 'US' + c.size.us_size if size_type == 'US' else 'UK' + c.size.uk_size if size_type == 'UK' else 'EU' + c.size.eu_size if size_type == 'EU' else 'FREESIZE'} for c in foo.product_count.all()]
    def get_thumbnails(self, obj):
        return [{'id': t.id, 'url': t.image.url_100x100} for t in obj.images.all().order_by('id')]
    def get_image1(self, obj):
        return obj.images.all().order_by('id')[0].image.url_500x500 if obj.images.all().order_by('id') else None
    def get_parcel(self, obj):
        return True
    class Meta:
        model = ApprovedProduct
        depth = 1
        fields = ('no_of_products', 'user', 'id', 'title', 'image1', 'thumbnails','description', 'style', 'brand', 'original_price', 'upload_time','parcel',
                  'sale', 'listing_price', 'occasion', 'product_category', 'color', 'completed', 'age', 'condition', 'discount','pickup_address','send_pushnot')

class ZapUserDetailsSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField('get_user_detail')

    def get_user_detail(self, foo):
        return {'id': foo.id, 'num_of_products': foo.approved_product.count(), 'profile_pic': foo.profile.profile_pic, 'zap_username': foo.zap_username}

    class Meta:
        model = ZapUser
        fields = ('users',)


class OrderSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    ordered_product = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    seller_address = serializers.SerializerMethodField()
    buyer_address = serializers.SerializerMethodField()
    payment_mode = serializers.SerializerMethodField()
    pickup_orders_logistics = serializers.SerializerMethodField()
    delivery_order_logistics = serializers.SerializerMethodField()
    with_zapyle = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()
    delivery_partner = serializers.SerializerMethodField()
    pickup_partner = serializers.SerializerMethodField()
    return_delivery_partner = serializers.SerializerMethodField()
    def get_final_price(self, obj):
        return obj.final_price
    def get_ordered_product(self, obj):
        return {'title':obj.ordered_product.title,'image':obj.ordered_product.image.image.url_500x500,'id':obj.product.id}
    def get_seller(self, obj):
        return obj.consignor.user.zap_username
    def get_buyer(self, obj):
        return obj.transaction.consignee.user.zap_username
    def get_seller_address(sef, obj):
        return obj.consignor.name+' ({},{},{},{}) {}'.format(obj.consignor.address,obj.consignor.city,obj.consignor.state.name,obj.consignor.pincode,obj.consignor.phone)
    def get_buyer_address(self, obj):
        return obj.transaction.consignee.name+' ({},{},{},{}) {}'.format(obj.transaction.consignee.address,obj.transaction.consignee.city,obj.transaction.consignee.state.name,obj.transaction.consignee.pincode,obj.transaction.consignee.phone)
    def get_payment_mode(self, obj):
        return obj.transaction.payment_mode
    def get_pickup_orders_logistics(self, obj):
        return obj.order_logistic.filter(triggered_pickup=True).count()

    def get_delivery_order_logistics(self, obj):
        return LogisticsLog.objects.filter(pickup=False,logistics__orders=obj).count()
    def get_with_zapyle(self, obj):
        return obj.ordered_product.with_zapyle
    def get_platform(self, obj):
        return obj.transaction.platform
    def get_delivery_partner(self, obj):
        partner = ''
        if obj.order_logistic.first():
            partner = obj.order_logistic.first().product_delivery_partner
        return partner
    def get_pickup_partner(self, obj):
        partner = ''
        if obj.order_logistic.first():
            partner = obj.order_logistic.first().pickup_partner
        return partner
    def get_return_delivery_partner(self, obj):
        partner = ''
        if obj.order_logistic.count() > 1:
            partner = obj.order_logistic.last().product_delivery_partner
        return partner
    # def get_triggered_logistics(self, obj):
    #     return obj.order_logistic.count()
    # def get_product(self, foo):
    #     p = foo.product
    #     return {'title': p.title, 'image1': p.images.all().order_by('id')[0].image.url_100x100}

    # def get_status(self, foo):
    #     print '$'*100
    #     # if foo.returned:
    #     #     return "Returned"
    #     if foo.returnmodel.all() and foo.returnmodel.all()[0].approved:
    #         return "Return approved"
    #     if foo.returnmodel.all():
    #         return "Return requested"
    #     if foo.delivery_date:
    #         return "Delivered"
    #     else:
    #         return "Being Processed"

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'placed_at','ordered_product','final_price','seller','buyer','seller_address','buyer_address','payout_mode','order_status','product_verification','payout_mode','confirmed_with_buyer','confirmed_with_seller','payment_mode','pickup_orders_logistics','delivery_order_logistics','with_zapyle','platform','delivery_partner','pickup_partner','return_delivery_partner')

class AdminOrderSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    pickup_address = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    delivery_address = serializers.SerializerMethodField()
    payment_mode = serializers.SerializerMethodField()
    procurement = serializers.SerializerMethodField()
    verification = serializers.SerializerMethodField()
    buyer_shipment = serializers.SerializerMethodField()
    returns = serializers.SerializerMethodField()
    payout = serializers.SerializerMethodField()
    refund_against_cancel = serializers.SerializerMethodField()
    cancel = serializers.SerializerMethodField()

    def get_product(self, obj):
        ord_pro = obj.ordered_product
        # pdb.set_trace()
        try:
            product_id = obj.product.id
        except:
            product_id = 'NA'
        return {'id':product_id, 'title':ord_pro.title, 'image':ord_pro.image.image.url_500x500, 'listing_price':ord_pro.listing_price, 
                'total_price':obj.total_price(), 'final_price':obj.final_payable_price(), 'zapcash_used':obj.zapwallet_used}
    def get_seller(self, obj):
        name = obj.product.user.get_full_name() or obj.product.zapexclusiveuserdata_set.all()[0].account_holder or 'ST'
        email = obj.product.user.email or obj.product.zapexclusiveuserdata_set.all()[0].email or 'NA'
        phone = obj.consignor.phone or obj.product.zapexclusiveuserdata_set.all()[0].phone_number
        return {'name':name, 'email':email, 'phone':phone}

    def get_pickup_address(self, obj):
        address2 = obj.consignor.address2 or ''
        add = obj.consignor.name + ", " + obj.consignor.address + ", " + address2 or '' + ", " + obj.consignor.pincode + ", " + obj.consignor.phone +"." \
                if not obj.ordered_product.with_zapyle else 'Zapyle, RMZ Millenia, Tower B, 4th floor, Ulsoor, 560008.'
        return {'address': add, 'confirmed':obj.confirmed_with_seller}
    def get_buyer(self, obj):
        consignee = obj.transaction.consignee
        return {'name':consignee.name, 'email':consignee.user.email, 'phone':consignee.phone}
    def get_delivery_address(self, obj):
        # pdb.set_trace()
        consignee = obj.transaction.consignee
        address2 = consignee.address2 or ''
        add = consignee.name + ", " + consignee.address + ", " + address2 + ", " + consignee.pincode + ", " + consignee.phone +"."
        return {'address':add, 'confirmed':obj.confirmed_with_buyer}
    def get_payment_mode(self, obj):
        return obj.transaction.payment_mode
    def get_procurement(self, obj):
        logistic_partner_dict = dict(LOGISTICS_PARTNERS)
        triggered = False if obj.order_status == 'confirmed' else True
        show = False 
        if obj.order_logistic.all():
            logistic = obj.order_logistic.all()[0]
            all_pickup_logistic_log = logistic.logistics_log.filter(pickup=True)
            if logistic.pickup_partner and all_pickup_logistic_log:
                log = all_pickup_logistic_log[0]
                updated_time = log.updated_time + timedelta(minutes=330)
                admin_status = dict(ADMIN_STATUS)
                status = admin_status.get(log.log_status, 'NA')
                show = True
        return {'status':status,'triggered':triggered, 'partner':logistic_partner_dict.get(logistic.pickup_partner,'NA'), 'updated_time':str(updated_time)} if show else {}
    def get_verification(self,obj):
        verify = True if obj.order_status == 'verification' and not obj.product_verification else False
        return {'status':obj.product_verification, 'verify':verify}
    def get_buyer_shipment(self, obj):
        logistic_partner_dict = dict(LOGISTICS_PARTNERS)
        show = False
        if obj.order_logistic.all():
            logistic = obj.order_logistic.all()[0]
            triggered = True
            if obj.ordered_product.with_zapyle:
                if logistic.triggered_pickup == False:
                    triggered = False
            elif logistic.triggered_pickup:
                log = logistic.logistics_log.filter(pickup=True)[0]
                if log.track:
                    triggered = False
            if triggered:
                delivery_logistic_log = logistic.logistics_log.filter(pickup=False)
                current_delivery_log = delivery_logistic_log[len(delivery_logistic_log)-1]
                updated_time = current_delivery_log.updated_time + timedelta(minutes=330)
                admin_status = dict(ADMIN_STATUS)
                status = admin_status.get(current_delivery_log.log_status, 'NA')
                show = True
        return {'status':status,'triggered':triggered, 'partner':logistic_partner_dict.get(logistic.product_delivery_partner,'NA'), 'updated_time':str(updated_time)} if show else {}
    def get_returns(self, obj):
        # pdb.set_trace()
        try:
            returns = obj.returnmodel
        except:
            returns = None
        if returns:
            if returns.approved:
                approved = False
        return {'approved': returns.approved} if returns else {}

    def get_payout(self, obj):
        return {'mode':obj.payout_mode or '', 'status': obj.payout_status or ''} if obj.order_status == 'delivered' else {}

    def get_refund_against_cancel(self, obj):
        return {'status':obj.refund_status} if obj.refund_status else {}

    def get_cancel(self, obj):
        return {'cancelled':True if obj.order_status == 'cancelled' else False}
    class Meta:
        model = Order
        fields = ('id', 'order_number','placed_at', 'cancel', 'product', 'seller', 'pickup_address', 'buyer', 'delivery_address',
                    'payment_mode', 'procurement', 'verification', 'buyer_shipment', 'returns', 'payout', 'refund_against_cancel')

    def to_representation(self, instance):
            ret = super(AdminOrderSerializer, self).to_representation(instance)
            # Here we filter the null values and creates a new dictionary
            # We use OrderedDict like in original method
            ret = OrderedDict(list(filter(lambda x: x[1], ret.items())))
            return ret


class ReturnSerializer(serializers.ModelSerializer):

    product = serializers.SerializerMethodField()
    logistic_partner = serializers.SerializerMethodField()
    triggered_logistics = serializers.SerializerMethodField()
    pickup_return_logistics = serializers.SerializerMethodField()
    delivery_return_logistics = serializers.SerializerMethodField()

    def get_product(self, foo):
        p = foo.order_id.ordered_product
        return {'title': p.title,
                'image1': p.image.image.url_100x100,
                'quantity': foo.order_id.quantity,
                'size': p.size,
                'order_number': foo.order_id.order_number,
                'final_price': foo.order_id.transaction.final_price}

    def get_logistic_partner(self, obj):
        partner = {}
        if obj.return_logistic.all():
            partner = {
                'pickup_partner' : obj.return_logistic.last().pickup_partner,
                'delivery_partner' : obj.return_logistic.last().product_delivery_partner,
            }
        return partner

    def get_triggered_logistics(self, obj):
        return  obj.return_logistic.count()

    def get_pickup_return_logistics(self, obj):
        return obj.return_logistic.filter(triggered_pickup=True).count()

    def get_delivery_return_logistics(self, obj):
        return LogisticsLog.objects.filter(pickup=False,logistics__returns=obj).count()

    class Meta:
        model = Return
        fields = ('id', 'product', 'reason', 'approved','return_status','logistic_partner', 'triggered_logistics', 'pickup_return_logistics', 'delivery_return_logistics')

# class AdminReturnSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField()
#     verification = serializers.SerializerMethodField()

#     def get_image(self, obj):
#         return self.order_id.ordered_product.image.image.url_500x500

#     def get_verification(self, obj):

#         verify = True if obj.return_logistic.last().logistic_log.filters(pickup=True)[0].log_status == 4 and not 
#         return {'status':}


#     model = Return
#     fields = ('id', 'order_id', 'image','approve', 'verification', 'refund')

class AdminLogisticsSerializer(serializers.ModelSerializer):

    orders = serializers.SerializerMethodField()
    returns = serializers.SerializerMethodField()

    products = serializers.SerializerMethodField()
    consignor = serializers.SerializerMethodField()
    consignee = serializers.SerializerMethodField()
    # logistic_partner = serializers.SerializerMethodField()
    pickup_partner = serializers.SerializerMethodField()
    product_delivery_partner = serializers.SerializerMethodField()

    def get_orders(self, obj):
        return [x.order_number for x in obj.orders.all()]
    def get_returns(self, obj):
        return [x.id for x in obj.returns.all()]
    def get_products(self, obj):
        return [{'image':i.product.images.all().order_by('id')[0].image.url_100x100, 'title':i.product.title} for i in obj.orders.all()]
    def get_consignor(self, obj):
        a = obj.consignor
        add = a.name +", "+a.address+", "+a.city+", "+a.state.name+", "+a.country+", "+a.pincode+". Phone-"+a.phone
        return {'userid':a.user.id,'full_address':add, 'address':[{'id':b.id, 'address':b.address} for b in Address.objects.filter(user=obj.consignor.user)], 'selected_address':a.id}
    def get_consignee(self, obj):
        ab = obj.consignee
        add = ab.name +", "+ab.address+", "+ab.city+", "+ab.state.name+", "+ab.country+", "+ab.pincode+". Phone-"+ab.phone
        return {'userid':ab.user.id,'full_address':add, 'address':[{'id':b.id, 'address':b.address} for b in Address.objects.filter(user=obj.consignee.user)], 'selected_address':ab.id}
    def get_pickup_partner(self, obj):
        logistic_partner_dict = dict(LOGISTICS_PARTNERS)
        return {'key':obj.pickup_partner, 'value':logistic_partner_dict.get(obj.pickup_partner)}
    def get_product_delivery_partner(self, obj):
        logistic_partner_dict = dict(LOGISTICS_PARTNERS)
        return {'key':obj.product_delivery_partner, 'value':logistic_partner_dict.get(obj.product_delivery_partner)}

    class Meta:
        model = Logistics
        field = '__all__'

        



class ZapExclusiveUserDataSerializer(serializers.ModelSerializer):
    product_approved_id = serializers.PrimaryKeyRelatedField(
        many=True, required=False, read_only=True)
    class Meta:
        model = ZapExclusiveUserData
        field = '__all__'
    # def update(self, instance, validated_data):
    #     added = validated_data.get('product_id', None)
    #     if added:
    #         instance.product_id.add(*added)
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.phone = validated_data.get('phone', instance.phone)
    #     instance.full_name = validated_data.get('full_name', instance.full_name)
    #     instance.ifsc_code = validated_data.get('ifsc_code', instance.ifsc_code)
    #     instance.save()
    #     return instance


class LogisticsLogRejectSerializer(serializers.ModelSerializer):
    logistics = serializers.SerializerMethodField()
    def get_logistics(self, obj):
        return LogisticsRejectSeriaizer(obj.logistics).data
    class Meta:
        model = LogisticsLog
        fields = ('logistics',)

class LogisticsRejectSeriaizer(serializers.ModelSerializer):
    class Meta:
        model = Logistics
        fields = ('orders','returns')

class ChangeUserProductSerlzr(serializers.ModelSerializer):
    zap_username = serializers.SerializerMethodField()
    def get_zap_username(self, obj):
        return (obj.zap_username or 'undefined')+' ('+(obj.email or 'undefined')+')'
    class Meta:
        model = ZapUser
        fields = ('id','zap_username')

class UpdateApprovedProductsSerializer(serializers.ModelSerializer):
    size_selected = serializers.SerializerMethodField()
    old_images = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    def get_size_selected(self, obj):
        return [{'id':s.id,'quantity':s.quantity,'size':str(s.size.id),'size_type':obj.size_type} for s in obj.product_count.all()]
    def get_old_images(self, obj):
        return [{'id':i.id,'image':i.image.url_100x100} for i in obj.images.all()]
    def get_user_detail(self, obj):
        return {'email':obj.user.zap_username+' ('+obj.user.email+')','id':'{},{}'.format(obj.user.id,obj.user.user_type.name)}
    class Meta:
        model = ApprovedProduct
        field = '__all__'
        
from zap_apps.zap_catalogue.models import *      
class SocialProductSerializer(serializers.Serializer):
    style = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Style.objects.all(), required=True)
    brand = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Brand.objects.all(), required=True)
    occasion = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Occasion.objects.all(), required=True)
    product_category = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=SubCategory.objects.all(), required=True)
    color = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Color.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=ZapUser.objects.all(), required=True)
    size_type = serializers.CharField(max_length=15, required=True)
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(min_length=20, required=True)

class SaleProductSerializer(serializers.Serializer):
    style = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Style.objects.all(), required=True)
    brand = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Brand.objects.all(), required=True)
    occasion = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Occasion.objects.all(), required=True)
    product_category = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=SubCategory.objects.all(), required=True)
    color = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Color.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=ZapUser.objects.all(), required=True)
    size_type = serializers.CharField(max_length=15, required=True)
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(min_length=20, required=True)

    original_price = serializers.FloatField(allow_null=False, required=True)
    listing_price = serializers.FloatField(allow_null=False, required=True)
    age = serializers.ChoiceField(allow_blank=False, allow_null=False, choices=[('0', '0-3 months'), ('1', '3-6 months'), ('2', '6-12 months'), ('3', '1-2 years')], required=True)
    condition = serializers.ChoiceField(allow_blank=False, allow_null=False, choices=[('0', 'New with tags'), ('1', 'Mint Condition'), ('2', 'Gently loved'), ('3', 'Worn out')], required=True)
    pickup_address = serializers.PrimaryKeyRelatedField(allow_null=False, queryset=Address.objects.all(), required=True)
    
    # size = PrimaryKeyRelatedField(many=True, read_only=True)
class UserProfileSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    pic = serializers.SerializerMethodField()
    zap_username = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    product_details = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    admiring_count = serializers.SerializerMethodField()
    admires_count = serializers.SerializerMethodField()
    pta_count =  serializers.SerializerMethodField()
    dp_count =  serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    return_count = serializers.SerializerMethodField()
    def get_user_type(self, obj):
        return True#[{'id':s.id,'quantity':s.quantity,'size':str(s.size.id),'size_type':obj.size_type} for s in obj.product_count.all()]
    def get_pic(self, obj):
        return obj.profile.profile_pic
    def get_zap_username(self, obj):
        return obj.zap_username
    def get_description(self, obj):
        return obj.profile.description
    def get_product_count(self, obj):
        return obj.approved_product(manager='ap_objects').count()
    def get_admiring_count(self, foo):
        return UserProfile.objects.filter(admiring__in=[foo.profile.user.id]).count()

    def get_admires_count(self, foo):
        return foo.profile.admiring.count()
    def get_pta_count(self, obj):
        return obj.product_to_approve.count()
    def get_dp_count(self, obj):
        return obj.disapproved_product.count()
    def get_order_count(self, obj):
        return Order.objects.filter(transaction__buyer=obj).count()
    def get_return_count(self, obj):
        return Return.objects.filter(order_id__transaction__buyer=obj).count()
    def get_product_details(self, obj):
       return UserProductSerializer(obj.approved_product.all(), many=True,
                                         context={'logged_user': obj}).data
    class Meta:
        model = ZapUser
        fields = ('id','pic','user_type','zap_username','product_count','product_details','description','admiring_count','admires_count','pta_count','dp_count','order_count','return_count')

class UserProductSerializer(serializers.ModelSerializer):
    commentCount = serializers.SerializerMethodField('get_comments_count')
    likesCount = serializers.SerializerMethodField('get_likes_count')
    liked_by_user = serializers.SerializerMethodField('liked_by_users')
    size = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    def get_discount(self, obj):
        if obj.sale == '2' and not obj.discount:
            return 'Not Approved'
        return str(int(obj.discount*100))+'% off' if obj.sale=='2' else 'Inspiration'
    def get_size(self, obj):
        size = ''
        if obj.size_type == 'FREESIZE':
            if obj.product_count.get(size__category_type="FS").quantity > 0:
                size = 'FREESIZE'
        else:
            for s in obj.size.all():
                if obj.product_count.get(size=s).quantity > 0 :
                    size+= 'UK'+s.uk_size+' '
        return size
    def get_comments_count(self, foo):
        return foo.comments_got.count()

    def get_likes_count(self, foo):
        return foo.likes_got.count()

    def liked_by_users(self, foo):
        logged_user = self.context['logged_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.loves.all():
                return True
            else:
                return False
        else:
            return False
    def get_images(self, obj):
        return [{'id':i.id, 'image': i.image.url_500x500} for i in obj.images.all().order_by('id')]

    class Meta:
        model = ApprovedProduct
        depth = 1
        fields = ('id', 'commentCount', 'likesCount', 'liked_by_user', 'images', 'title',
                  'original_price', 'discount', 'listing_price', 'sale', 'brand', 'style','size')

class NotifsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifs
        field = '__all__'

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        field = '__all__'

class AdminSingleApprovedProducSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    commentCount = serializers.SerializerMethodField('get_comments_count')
    likesCount = serializers.SerializerMethodField('get_likes_count')
    liked_by_user = serializers.SerializerMethodField('liked_by_users')
    # comments = serializers.SerializerMethodField('get_full_comments')
    user = serializers.SerializerMethodField('user_details')
    no_of_products = serializers.SerializerMethodField('get_products_count')
    num_products_of_user = serializers.SerializerMethodField(
        'get_user_num_products')
    age = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    condition = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()
    occasion = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    admired_by_user = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    deletable = serializers.SerializerMethodField()
    size_type = serializers.SerializerMethodField()
    flash_sale_data = serializers.SerializerMethodField()
    listing_price = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()

    def get_shop(self, obj):
        return SHOP_NAME[obj.shop]
        
    def get_title(self, foo):
        return foo.get_title()

    def get_size_type(self, foo):
        return foo.size_type or (
            "UK" if foo.product_category.parent.category_type == 'C' else
            "US" if foo.product_category.parent.category_type == 'FW' else "FREESIZE")

    def get_deletable(self, foo):
        return True if hasattr(foo, "ordered_product") and foo.ordered_product.count() == 0 else False

    def get_available(self, obj):
        return False if obj.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] <= 0 or obj.sale == '1' else True

    def get_size(self, obj):
        # if obj.product_count.get(size=s).quantity>0
        return [{'id': s.id, 'size': s.size, 'uk_size': s.uk_size, 'us_size': s.us_size, 'eu_size': s.eu_size, 'category_type': s.category_type, 'quantity': obj.product_count.get(size=s).quantity} for s in obj.size.all().extra(select={'i': 'CAST(uk_size AS FLOAT)'}).order_by('i')]

    def get_discount(self, foo):
        if foo.discount != '' and foo.discount != None and foo.discount != 0:
            return int(foo.discount*100) if foo.discount else None
        else:
            return None

    def get_sale(self, foo):
        return foo.get_sale_display()

    def get_style(self, foo):
        return foo.style.style_type if foo.style else None

    def get_brand(self, foo):
        return foo.brand.brand

    def get_occasion(self, foo):
        return foo.occasion.name if foo.occasion else None

    def get_color(self, foo):
        return foo.color.name if foo.color else None

    def get_product_category(self, foo):
        return foo.product_category.name

    def get_images(self, obj):
        return [i.image.url_1000x1000 for i in obj.images.all().order_by('id')]

    def get_age(self, obj):
        return obj.get_age_display()

    def get_condition(self, obj):
        return obj.get_condition_display()

    def get_comments_count(self, foo):
        return foo.comments_got.count()

    def get_likes_count(self, foo):
        return foo.likes_got.count()

    def liked_by_users(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            return True if logged_user in foo.loves.all() else False
        else:
            return False

    # def get_full_comments(self, foo):
    #     srlzr = CommentsSerializer(foo.comments_got.all(), many=True)
    #     return srlzr.data

    def user_details(self, foo):
        version = self.context['version']
        # if foo.user.user_type.name in ['zap_exclusive']:
        #     user_data = {'id': str(foo.user.id), 'user_type': str(foo.user.user_type.name)}
        #     return user_data
        if 'version' in version and int(version['version']) > 1:
            if foo.user.user_type.name in ['zap_exclusive']:
                # user_data = {'id': str(foo.user.id), 'user_type': str(foo.user.user_type.name)}
                return None
        return AndroidUserSerializer(foo.user).data

    def get_user_num_products(self, foo):
        return foo.user.approved_product(manager='ap_objects').count()

    def get_products_count(self, foo):
        return [{'size_id': product.size.id, 'quantity': product.quantity} for product in foo.product_count.all()]

    def get_admired_by_user(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            return True if logged_user in foo.user.profile.admiring.all() else False
        else:
            return False
    sold_out = serializers.SerializerMethodField()

    def get_sold_out(self, foo):
        return False if foo.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else True
    shipping_charge = serializers.SerializerMethodField()

    def get_shipping_charge(self, foo):
        return settings.SHIPPING_CHARGE if foo.listing_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0

    def get_listing_price(self, obj):
        return obj.listing_price

    def get_flash_sale_data(self, obj):
        from zap_apps.marketing.models import CampaignProducts, Campaign
        running_campaign = Campaign.objects.filter(offer__end_time__gt=timezone.now(), offer__start_time__lt=timezone.now(), campaign_product__products=obj.id).first()
        if running_campaign:
            campaign_product = CampaignProducts.objects.filter(products=obj.id, campaign=running_campaign)[0]
            timediff = running_campaign.offer.end_time.replace(tzinfo=None) - datetime.datetime.now().replace(tzinfo=None)
            return {'sale_name': running_campaign.name,
                    'end_timestamp': (running_campaign.offer.end_time.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds(),
                    'end_time': timediff.days * 86400 + timediff.seconds, 'show_timer': running_campaign.offer.show_timer,
                    'before_flash_sale_price': obj.listing_price, 'original_discount': int(obj.discount*100),
                    'extra_discount': int(campaign_product.discount)}
        else:
            return None
    def get_category(self, obj):
        return obj.product_category.parent.name
    class Meta:
        model = ApprovedProduct
        fields = ('title', 'shipping_charge', 'num_products_of_user', 'no_of_products',
            'size', 'id', 'user', 'title', 'description', 'commentCount', 'likesCount', 
            'liked_by_user', 'images', 'size_type', 'sale', 'product_category', 'partner_id',
            'original_price', 'listing_price', 'discount', 'upload_time', 'style', 'shop',
            'brand', 'occasion', 'color', 'age', 'condition', 'admired_by_user', 'with_zapyle',
            'sold_out', 'available', 'deletable', 'best_price', 'time_to_make', 'flash_sale_data',
            'category', 'percentage_commission')

SHOP_NAME = {
    1:'designer',
    2:'curated',
    3:'market',
    4:'brand',
    7:'highstreet'
}

class ElasticProductsSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    love_count = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    i_category = serializers.SerializerMethodField()
    i_product_category = serializers.SerializerMethodField()
    i_style = serializers.SerializerMethodField()
    i_color = serializers.SerializerMethodField()
    i_occasion = serializers.SerializerMethodField()
    i_brand = serializers.SerializerMethodField()
    def get_category(self, obj):
        return obj.product_category.parent.id
    def get_available(self,obj):
        return True if obj.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else False
    def get_user_type(self, obj):
        return obj.user.user_type.name
    def get_image(self, obj):
        return settings.DOMAIN_NAME+obj.images.first().image.url_500x500
    def get_brand_name(self, obj):
        return obj.brand.brand
    def get_liked_by_user(self, obj):
        return False
    def get_shop(self, obj):
        return SHOP_NAME[obj.shop]
        # user_type = obj.user.user_type.name
        # if user_type == 'zap_exclusive':
        #     return 'curated'
        # elif user_type in ['zap_user', 'zap_dummy', 'zap_admin', 'store_front']:
        #     return 'market'
        # elif obj.user.representing_brand.designer_brand:
        #     return 'designer'
        # else:
        #     return 'brand'
    def get_discount(self, obj):
        if obj.discount != '' and obj.discount != None and obj.discount != 0:
            return int(obj.discount*100) if obj.discount else None
        return None
    def get_size(self, obj):
        return [s.id for s in obj.size.all()]
    def get_love_count(self, obj):
        return obj.loves.count()
    def get_category_name(self, obj):
        return obj.product_category.parent.name
    def get_i_category(self, obj):
        return obj.product_category.parent.slug
    def get_i_product_category(self, obj):
        return obj.product_category.slug
    def get_i_style(self, obj):
        return obj.style.slug if obj.style else None
    def get_i_color(self, obj):
        return obj.color.slug if obj.color else None
    def get_i_occasion(self, obj):
        return obj.occasion.slug if obj.occasion else None
    def get_i_brand(self, obj):
        return obj.brand.slug

    class Meta:
        model = ApprovedProduct
        fields = ('id', 'title', 'category', 'available', 'user_type', 'image', 'brand_name', 'listing_price', 'original_price',
            'discount', 'liked_by_user', 'shop', 'product_category', 'brand', 'condition', 'score', 'age', 'style', 'color', 'description',
            'occasion', 'size','love_count','i_category','i_product_category','i_style','i_color','i_occasion','i_brand','category_name')
