from rest_framework import serializers
from zap_apps.zapuser.models import ZapUser, UserPreference, UserData, UserProfile, WaistSize, City, DesignerProfile, Subscriber
from rest_framework.validators import UniqueValidator
from zap_apps.zap_catalogue.models import Loves, ApprovedProduct, Brand
from zap_apps.account.account_serializer import check_phone_number
from zap_apps.zap_notification.views import PushNotification
from zap_apps.order.models import Transaction, Order, Return, RETURN_REASONS
from zap_apps.zap_notification.models import Notification
from zap_apps.zap_commons.common_serializers import ZapErrorModelSrlzr, ZapErrorSrlzr
from zap_apps.zapuser.tasks import after_admire_notif
from django.conf import settings
import re
from django.db.models import Sum
from zap_apps.zap_catalogue.tasks import send_to_elasticsearch

pushnots = PushNotification()

SEX = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class ReturnSerializerPOST(serializers.Serializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    reason = serializers.ChoiceField(choices=RETURN_REASONS)


class UserInfoSerializer(ZapErrorSrlzr):
    #email = serializers.CharField()
    zap_username = serializers.CharField(
        required=False, max_length=30, min_length=6)
    #phone_number = serializers.CharField()
    full_name = serializers.CharField(required=False,)
    description = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(required=False, choices=SEX)
    selected_location_id = serializers.PrimaryKeyRelatedField(
        required=False, queryset=City.objects.all())
    dob = serializers.DateField(required=False, input_formats=(['%d-%m-%Y']))

    def save(self, user):
        if 'dob' in self.validated_data:
            if self.validated_data['dob'].year < 1900:
                raise serializers.ValidationError(
                    {"dob": "Invalid Date of Birth: atleast 1900"})
            user.profile.dob = self.validated_data['dob']
        if 'gender' in self.validated_data:
            user.profile.sex = self.validated_data['gender']
        if 'zap_username' in self.validated_data:
            zap_username = self.validated_data['zap_username']
            if ZapUser.objects.filter(zap_username=zap_username).exists() and not zap_username == user.zap_username:
                raise serializers.ValidationError(
                    {'zap_username': "Username already exists"})
            user.zap_username = self.validated_data['zap_username']
        if 'full_name' in self.validated_data:
            user.first_name = self.validated_data['full_name'].split()[0]
            try:
                user.last_name = ' '.join(self.validated_data['full_name'].split()[1:])
            except IndexError:
                user.last_name = ''
        if 'description' in self.validated_data:
            user.profile.description = self.validated_data['description']
        if 'selected_location_id' in self.validated_data:
            user.profile.city = self.validated_data['selected_location_id']
        user.profile.save()
        user.save()


class AdmireSrlzr(serializers.Serializer):
    action = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=ZapUser.objects.all())

    def validate_action(self, value):
        if value not in ['admire', 'unadmire']:
            raise serializers.ValidationError("action must be admire/unadmire")
        return value

    def save(self, current_user):
        user = self.validated_data['user']
        if self.validated_data['action'] == 'admire':
            user.profile.admiring.add(current_user)
            if settings.CELERY_USE:
                after_admire_notif.apply_async(args=[user.id, current_user.id], countdown=30)
            else:
                after_admire_notif(user.id, current_user.id)
            
            
        if self.validated_data['action'] == 'unadmire':
            user.profile.admiring.remove(current_user)
        return None


class CheckBuildNumberSlzr(serializers.Serializer):
    number = serializers.IntegerField()


class DescriptionSlzr(serializers.Serializer):
    description = serializers.CharField(max_length=1000)


class PhoneNumSrlzr(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=ZapUser.objects.all(), message="Phone number already exists.")])

    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return data
    class Meta:
        model = ZapUser
        fields = ('phone_number',)

class PhoneNumSrlzrOTP(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return data

class PhoneNumWithOtpSrlzr(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.IntegerField()

    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Please enter a valid phone number.")
        return data

class OTPSrlzr(serializers.Serializer):
    otp = serializers.IntegerField()

class WaistSizeSrlzr(serializers.ModelSerializer):

    class Meta:
        model = WaistSize
        field = '__all__'

class CheckEmailNum(serializers.Serializer):
    email = serializers.EmailField(max_length=30, min_length=6 ,validators=[
                                         UniqueValidator(queryset=ZapUser.objects.all(), message="Email ID already exists.")])
    phone_number = serializers.CharField(min_length=10, max_length=14, validators=[
                                        UniqueValidator(queryset=ZapUser.objects.all(), message="Phone Number already exists.")])
    zap_username = serializers.CharField(min_length=4, max_length=30, validators=[
                                         UniqueValidator(queryset=ZapUser.objects.all(), message="Username already exists.")])
    def validate_zap_username(self, data):
        if not re.match("^[a-zA-Z0-9_]+$", data):
            raise serializers.ValidationError(
                "Username only allows alphabets and numbers without space.")
        if re.match("^[0-9]+$", data):
            raise serializers.ValidationError(
                "Username must contain at least one alphabet.")
        return data

    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return data

class CheckUsernameSrlzr(serializers.Serializer):
    zap_username = serializers.CharField(max_length=30, min_length=6, validators=[
                                         UniqueValidator(queryset=ZapUser.objects.all(), message="Username already exists.")])
    #email = serializers.EmailField(max_length=30, min_length=6)
    # def validate_email(self, data):
    #     if ZapUser.objects.filter(email=data):
    #         if not data == self.context['user'].email:
    #             raise serializers.ValidationError("This email is already registered.")
    #     return data


class UserDataSerializer(ZapErrorSrlzr):
    account_number = serializers.IntegerField()
    account_holder = serializers.CharField(min_length=4, max_length=30 ,required=False)
    ifsc_code = serializers.CharField(min_length=5, max_length=20)
    class Meta:
        model = UserData
        field = ('user', 'account_number',
                 'ifsc_code', 'fb_friends_list', 'old_account_number', 'old_ifsc_code','account_holder')


from django.core.cache import cache
class LikeUnlikeSlzr(serializers.Serializer):
    action = serializers.CharField(max_length=10)
    product_id = serializers.IntegerField()

    def validate_action(self, data):
        if not data in ['like', 'unlike']:
            raise serializers.ValidationError("action should be like/unlike")
        return data

    def save(self, current_user, product):
        if self.validated_data['action'] == "like":
            Loves.objects.get_or_create(product=product, loved_by=current_user)
        if self.validated_data['action'] == "unlike":
            Loves.objects.filter(
                product=product, loved_by=current_user).delete()
        cache.clear()
        if settings.CELERY_USE:
            send_to_elasticsearch.delay(product)
        else:
            send_to_elasticsearch(product)
        return None

class ProfileDetailsSerializerV2(serializers.ModelSerializer):
    # profile_pic = serializers.SerializerMethodField('profile_picture')
    outfits = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    # admiring = serializers.SerializerMethodField('admiring_count')
    admirers = serializers.SerializerMethodField()
    admire_or_not = serializers.SerializerMethodField()
    # description = serializers.SerializerMethodField()
    seller_type = serializers.SerializerMethodField()
    designer_details = serializers.SerializerMethodField()

    def get_designer_details(self, foo):
        from django.core.exceptions import ObjectDoesNotExist
        if foo.user_type.name == 'designer':
            try:
                designer_details = Brand.objects.get(brand_account=foo.id)
                return {'description': str(designer_details.description),
                        'description_short': str(designer_details.description_short),
                        'cover_pic': ('/zapmedia/' + str(designer_details.mobile_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=600',
                        'web_cover_pic': ('/zapmedia/' + str(designer_details.web_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=800'}
            except ObjectDoesNotExist:
                return None
        else:
            return None

    def get_seller_type(self, foo):
        if foo.user_type.name == 'designer':
            return 'Designer'
        elif foo.user_type.name == 'zap_exclusive':
            return 'Curated'
        else:
            return 'Market'

    # def get_description(self, foo):
    #     return foo.profile.description

    # def profile_picture(self, foo):
    #     return foo.profile.profile_pic

    def get_outfits(self, obj):
        return obj.approved_product(manager='ap_objects').count()

    def get_products(self, foo):
        prod_type = self.context['type']
        if prod_type == 'both':
            return WebProfileProductsSerializer(foo.approved_product(manager='ap_objects').all(), many=True,
                                         context={'logged_user': self.context['current_user']}).data
        elif prod_type == 'inspiration':
            return WebProfileProductsSerializer(foo.approved_product(manager='ap_objects').filter(sale='1'), many=True,
                                         context={'logged_user': self.context['current_user']}).data
        else:
            return WebProfileProductsSerializer(foo.approved_product(manager='ap_objects').filter(sale='2'), many=True,
                                         context={'logged_user': self.context['current_user']}).data

    # def admiring_count(self, foo):
    #     return UserProfile.objects.filter(admiring__in=[foo.profile.user.id]).count()
    user_type = serializers.SerializerMethodField()
    def get_user_type(obj, foo):
        return foo.user_type.name if foo.user_type.name != 'designer' else 'store_front'
    def get_admirers(self, obj):
        return obj.profile.admiring.count()

    def get_admire_or_not(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.profile.admiring.all():
                return True
            else:
                return False
        else:
            return False

    class Meta:
        model = ZapUser
        fields = ('id','admirers','outfits','products','admire_or_not','user_type', 'seller_type', 'designer_details')

class ProfileDetailsSerializer(serializers.ModelSerializer):
    # profile_pic = serializers.SerializerMethodField('profile_picture')
    outfits = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    # admiring = serializers.SerializerMethodField('admiring_count')
    admirers = serializers.SerializerMethodField()
    admire_or_not = serializers.SerializerMethodField()
    # description = serializers.SerializerMethodField()
    seller_type = serializers.SerializerMethodField()
    designer_details = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    def get_designer_details(self, foo):
        from django.core.exceptions import ObjectDoesNotExist
        if foo.user_type.name == 'designer':
            try:
                designer_details = Brand.objects.get(brand_account=foo.id)
                return {'description': str(designer_details.description),
                        'description_short': str(designer_details.description_short),
                        'cover_pic': ('/zapmedia/' + str(designer_details.mobile_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=600',
                        'web_cover_pic': ('/zapmedia/' + str(designer_details.web_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=800'}
            except ObjectDoesNotExist:
                return None
        else:
            return None

    def get_seller_type(self, foo):
        if foo.user_type.name == 'designer':
            return 'Designer'
        elif foo.user_type.name == 'zap_exclusive':
            return 'Curated'
        else:
            return 'Market'

    # def get_description(self, foo):
    #     return foo.profile.description

    # def profile_picture(self, foo):
    #     return foo.profile.profile_pic

    def get_outfits(self, obj):
        return obj.approved_product(manager='ap_objects').count()

    def get_products(self, foo):
        prod_type = self.context['type']
        if prod_type == 'both':
            return WebProfileProductsSerializer(foo.approved_product(manager='ap_objects').all(), many=True,
                                         context={'logged_user': self.context['current_user']}).data
        elif prod_type == 'inspiration':
            return WebProfileProductsSerializer(foo.approved_product(manager='ap_objects').filter(sale='1'), many=True,
                                         context={'logged_user': self.context['current_user']}).data
        else:
            return WebProfileProductsSerializer(foo.approved_product(manager='ap_objects').filter(sale='2'), many=True,
                                         context={'logged_user': self.context['current_user']}).data
    # def admiring_count(self, foo):
    #     return UserProfile.objects.filter(admiring__in=[foo.profile.user.id]).count()
    def get_user_type(obj, foo):
        return foo.user_type.name
    def get_admirers(self, obj):
        return obj.profile.admiring.count()

    def get_admire_or_not(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.profile.admiring.all():
                return True
            else:
                return False
        else:
            return False

    class Meta:
        model = ZapUser
        fields = ('id','admirers','outfits','products','admire_or_not','user_type', 'seller_type', 'designer_details')


class AndroidProfileDetailsSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('profile_picture')
    no_of_posts = serializers.SerializerMethodField('get_posts_count')
    posts = serializers.SerializerMethodField('get_product_details')
    admiring = serializers.SerializerMethodField('admiring_count')
    admirers = serializers.SerializerMethodField('admirers_count')
    admired_by_user = serializers.SerializerMethodField('check_admire_or_not')
    description = serializers.SerializerMethodField()
    seller_type = serializers.SerializerMethodField()
    designer_details = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    def get_designer_details(self, foo):
        from django.core.exceptions import ObjectDoesNotExist
        if foo.user_type.name == 'designer':
            try:
                designer_details = Brand.objects.get(brand_account=foo.id)
                return {'description': str(designer_details.description),
                        'description_short': str(designer_details.description_short),
                        'cover_pic': ('/zapmedia/' + str(designer_details.mobile_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=600',
                        'web_cover_pic': ('/zapmedia/' + str(designer_details.web_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=800'}
            except ObjectDoesNotExist:
                return None
        else:
            return None

    def get_seller_type(self, foo):
        if foo.user_type.name == 'designer':
            return 'Designer'
        elif foo.user_type.name == 'zap_exclusive':
            return 'Curated'
        else:
            return 'Market'

    def get_description(self, foo):
        return foo.profile.description
    def profile_picture(self, foo):
        return foo.profile.profile_pic
    # def profile_picture(self, foo):
    #     return foo.profile.pro_pic.url_500x500 if (hasattr(foo.profile, 'pro_pic') and foo.profile.pro_pic) else foo.profile.profile_pic

    def get_posts_count(self, foo):
        return foo.approved_product(manager='ap_objects').count()

    def get_product_details(self, foo):
        posts1 = [{'p_t_a': False, "image_url": i.images.all().order_by('id')[0].image.url_500x500 if i.images.all(
        ) else "", 'id': i.id, 'sale': True if i.sale == '2' else False, 'title':i.get_title(), 'original_price':i.original_price, 'brand':i.brand.brand if i.brand else '',
        'listing_price': i.listing_price, 'discount':"{}".format(int(i.discount*100) if i.discount else 0), 'love_count':i.loves.count(),
        'loved_by_user': foo in i.loves.all()} for i in foo.approved_product(manager='ap_objects').all()]
        if self.context['current_user'].is_authenticated() and self.context['current_user'].id==foo.id:
            posts2 = [{'p_t_a': True, "image_url": i.images.all().order_by('id')[0].image.url_500x500 if i.images.all() else "", 'id': i.id, 'sale': True if i.sale ==
                    '2' else False, 'title':i.get_title(), 'original_price':i.original_price, 'brand':i.brand.brand if i.brand else '',
                    'listing_price': i.listing_price, 'discount':"{}".format(int(i.discount*100) if i.discount else 0), 'love_count':i.loves.count(),
                    'loved_by_user': foo in i.loves.all()} for i in ApprovedProduct.pta_objects.filter(user=self.context['current_user'])]
        else:
            posts2 = []
        return posts1 + posts2

    def admiring_count(self, foo):
        return UserProfile.objects.filter(admiring__in=[foo.profile.user.id]).count()

    def admirers_count(self, foo):
        return foo.profile.admiring.count()

    def check_admire_or_not(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.profile.admiring.all():
                return True
            else:
                return False
        else:
            return False
    def get_user_type(obj, foo):
        return foo.user_type.name if foo.user_type.name != 'designer' else 'store_front'

    class Meta:
        model = ZapUser
        fields = ('description', 'id', 'zap_username', 'profile_pic',
                  'no_of_posts', 'posts', 'admirers', 'admiring', 'admired_by_user','user_type', 'seller_type', 'designer_details')

class AndroidProfileDetailsSerializerV2(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('profile_picture')
    no_of_posts = serializers.SerializerMethodField('get_posts_count')
    posts = serializers.SerializerMethodField('get_product_details')
    admiring = serializers.SerializerMethodField('admiring_count')
    admirers = serializers.SerializerMethodField('admirers_count')
    admired_by_user = serializers.SerializerMethodField('check_admire_or_not')
    description = serializers.SerializerMethodField()
    seller_type = serializers.SerializerMethodField()
    designer_details = serializers.SerializerMethodField()

    def get_designer_details(self, foo):
        from django.core.exceptions import ObjectDoesNotExist
        if foo.user_type.name == 'designer':
            try:
                designer_details = Brand.objects.get(brand_account=foo.id)
                return {'description': str(designer_details.description),
                        'description_short': str(designer_details.description_short),
                        'cover_pic': ('/zapmedia/' + str(designer_details.mobile_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=600',
                        'web_cover_pic': ('/zapmedia/' + str(designer_details.web_cover)) if designer_details.designer_brand else designer_details.clearbit_logo + '?s=800'}
            except ObjectDoesNotExist:
                return None
        else:
            return None

    def get_seller_type(self, foo):
        if foo.user_type.name == 'designer':
            return 'Designer'
        elif foo.user_type.name == 'zap_exclusive':
            return 'Curated'
        else:
            return 'Market'

    def get_description(self, foo):
        return foo.profile.description
    def profile_picture(self, foo):
        return foo.profile.profile_pic
    # def profile_picture(self, foo):
    #     return foo.profile.pro_pic.url_500x500 if (hasattr(foo.profile, 'pro_pic') and foo.profile.pro_pic) else foo.profile.profile_pic

    def get_posts_count(self, foo):
        return foo.approved_product(manager='ap_objects').count()

    def get_product_details(self, foo):
        uploaded_by = {
            'id': foo.id,
            'zap_username': foo.zap_username,
            'profile_pic': foo.profile.profile_pic,
            'user_type': foo.user_type.name
        }
        posts1 = [{'p_t_a': False, "images": [i.images.all().order_by('id')[0].image.url_500x500] if i.images.all(
        ) else [""], 'style': i.style.style_type if i.style else None, 'id': i.id, 'sale': 'SALE' if i.sale == '2' else 'SOCIAL',
                   'title':i.get_title(), 'original_price':i.original_price, 'brand': i.brand.brand if i.brand else '',
                   'available': True if i.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else False,
                   'listing_price': i.listing_price, 'discount':int(i.discount*100 if i.discount else 0),
                   'likes_count':i.loves.count(), 'comment_count': i.comments_got.count(), 'size_type': i.size_type,
                   'sold_out': False if i.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else True,
                   'uploaded_by':uploaded_by,
                   'liked_by_user': True if foo in i.loves.all() else False}
                   for i in foo.approved_product(manager='ap_objects').all()]
        if self.context['current_user'].is_authenticated() and self.context['current_user'].id==foo.id:
            posts2 = [{'p_t_a': True, "images": [i.images.all().order_by('id')[0].image.url_500x500] if i.images.all(
                     ) else [""], 'id': i.id, 'sale': 'SALE' if i.sale == '2' else 'SOCIAL', 'style': i.style.style_type if i.style else None,
                    'title':i.get_title(), 'original_price':i.original_price, 'brand': i.brand.brand if i.brand else '',
                    'available': True if i.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else False,
                    'listing_price': i.listing_price, 'discount':int(i.discount*100 if i.discount else 0),
                    'likes_count':i.loves.count(),'comment_count': i.comments_got.count(), 'size_type': i.size_type,
                    'sold_out': False if i.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else True,
                    'uploaded_by':uploaded_by,
                    'liked_by_user': True if foo in i.loves.all() else False}
                    for i in ApprovedProduct.pta_objects.filter(user=self.context['current_user'])]
        else:
            posts2 = []
        return posts1 + posts2

    def admiring_count(self, foo):
        return UserProfile.objects.filter(admiring__in=[foo.profile.user.id]).count()

    def admirers_count(self, foo):
        return foo.profile.admiring.count()

    def check_admire_or_not(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.profile.admiring.all():
                return True
            else:
                return False
        else:
            return False
    user_type = serializers.SerializerMethodField()
    def get_user_type(obj, foo):
        return foo.user_type.name if foo.user_type.name != 'designer' else 'store_front'

    class Meta:
        model = ZapUser
        fields = ('description', 'id', 'zap_username', 'profile_pic',
                  'no_of_posts', 'posts', 'admirers', 'admiring', 'admired_by_user','user_type', 'seller_type', 'designer_details')

class WebProfileProductsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField("get_number_of_products")
    def get_title(self, obj):
        return ((obj.color.name + ' ') if obj.color else (
            obj.style.style_type + ' ') if obj.style else '') + obj.product_category.name if obj.user.user_type.name != 'designer' else obj.title
    def get_images(self, obj):
        return [{'id':i.id, 'image': i.image.url_500x500} for i in obj.images.all().order_by('id')]
    def get_discount(self, obj):
        if obj.sale == '2' and not obj.discount:
            return 'Not Approved'
        return str(int(obj.discount*100))+'% off' if obj.sale=='2' else 'Inspiration'
    def get_liked(self, foo):
        logged_user = self.context['logged_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.loves.all():
                return True
            else:
                return False
        else:
            return False
    def get_number_of_products(self, foo):
        return True if foo.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else False
    class Meta:
        model = ApprovedProduct
        depth = 1
        fields = ('id', 'images','title', 'listing_price','original_price','discount','liked', 'available')

class ApprovedProductSerializer(serializers.ModelSerializer):
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


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('profile_picture')
    # product_images = serializers.SerializerMethodField()
    admired = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    def get_user_id(self, foo):
        return foo.id
    def get_full_name(self,foo):
        return foo.get_full_name()
    def get_admired(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.profile.admiring.all():
                return True
            else:
                return False
        else:
            return False

    # def get_product_images(self, foo):
    #     return [{'url': i.images.all()[0].image.url_500x500, 'id':i.id} for i in ApprovedProduct.ap_objects.filter(user=foo)[0:4]]

    def profile_picture(self, foo):
        return foo.profile.profile_pic

    class Meta:
        model = ZapUser
        fields = ('user_id', 'zap_username', 'profile_pic', 'admired', 'full_name')#, 'product_images')


class MentionSerializer(serializers.ModelSerializer):

    profile_pic = serializers.SerializerMethodField('profile_picture')
    full_name = serializers.SerializerMethodField()
    
    def profile_picture(self, foo):
        return foo.profile.profile_pic

    def get_full_name(self,foo):
        return foo.get_full_name()

    class Meta:
        model = ZapUser
        fields = ('full_name','zap_username', 'profile_pic')


class SubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscriber
        fields = ('name', 'email', 'phone_number', 'monthly_spend', 'brands')
