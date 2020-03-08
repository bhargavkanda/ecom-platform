from rest_framework import serializers
from zap_apps.address.models import State

from zap_apps.zap_catalogue.models import (Size, Product, ProductImage, Category, SubCategory,
                                           Occasion, Color, Brand, Size, Style, ApprovedProduct, Comments, Loves, NumberOfProducts, Conversations, ZapCuratedEntry)
from zap_apps.zapuser.models import ZapUser
import re
from django.utils import timesince, timezone
from django.conf import settings
from zap_apps.zapuser.models import UserProfile
from django.db.models import Sum
import datetime
from django.db.models import Q


class WebsiteProductSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    condition = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    thumbnails = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    listing_price = serializers.SerializerMethodField()
    cashback = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.get_title()
    def get_listing_price(self, obj):
        return obj.get_offer_price()
    def get_brand(self, obj):
        return obj.brand.brand
    def get_age(self, obj):
        return obj.get_age_display()
    def get_condition(self, obj):
        return obj.get_condition_display()
    def get_image(self, obj):
        return obj.images.all().order_by('id')[0].image.url_1000x1000
    def get_thumbnails(self, obj):
        return [{'id': t.id, 'url': t.image.url_100x100} for t in obj.images.all().order_by('id')]
    def get_size(self, obj):
        size_type = obj.size_type or (
            "UK" if obj.product_category.parent.category_type == 'C' else
            "US" if obj.product_category.parent.category_type == 'FW' else "FREESIZE")
        if size_type == 'UK':
            return [{'size':size_type+s.uk_size, 'qty':obj.product_count.get(size=s).quantity, 'id':s.id, 'tooltip':"UK-{}  (Size: {}   |   US-{}   |   EU-{})".format(s.uk_size,s.size,s.us_size,s.eu_size)} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i')]# if obj.product_count.get(size=s).quantity>0]
        elif size_type == 'US':
            return [{'size':size_type+s.us_size, 'qty':obj.product_count.get(size=s).quantity, 'id':s.id, 'tooltip':"US-{}  (Size: {}   |   UK-{}   |   EU-{})".format(s.us_size,s.size,s.uk_size,s.eu_size)} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i')]# if obj.product_count.get(size=s).quantity>0]
        elif size_type == 'EU':
            return [{'size':size_type+s.eu_size, 'qty':obj.product_count.get(size=s).quantity, 'id':s.id, 'tooltip':"EU-{}  (Size: {}   |   UK-{}   |   US-{})".format(s.eu_size,s.size,s.uk_size,s.us_size)} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i')]# if obj.product_count.get(size=s).quantity>0]
        else:
            return [{'size':'FREESIZE','qty':obj.product_count.get(size=s).quantity, 'id':s.id} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i') if obj.product_count.get(size=s).quantity>0]

    def get_discount(self, obj):
        if obj.discount != '' and obj.discount != None and obj.discount != 0:
            return str(int(obj.discount*100))+'% off' if obj.sale=='2' else 'Inspiration'
        else:
            return None

    def get_available(self, obj):
        return True if obj.product_count.filter(quantity__gt=0) else False

    def get_cashback(self, obj):
        return int(obj.cashback.value) if obj.cashback else 0

    class Meta:
        model = ApprovedProduct
        fields = ('id', 'title','original_price','listing_price','discount','description','age','condition','brand','image','thumbnails','size','user','available', 'time_to_make', 'cashback')


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ('id', 'name')


class GetCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type', 'meta_description', 'web_cover', 'mobile_cover')


class SubCategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    def get_parent(self, foo):
        return {
            'id': foo.parent.id,
            'name': foo.parent.name,
            'category_type': foo.category_type}

    class Meta:
        model = SubCategory
        depth = 1
        fields = ('id', 'name', 'parent', 'meta_description', 'mobile_cover', 'web_cover')


class OccasionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Occasion
        fields = ('id', 'name')


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = ('id', 'name')


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('id', 'brand', 'meta_description', 'web_cover', 'mobile_cover', 'slug', 'clearbit_logo')


class SizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        fields = ('id', 'size', 'uk_size', 'us_size',
                  'eu_size', 'category_type')


class StyleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Style
        fields = ('id', 'style_type')


class ZapProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApprovedProduct
        field = '__all__'


class ProductsToApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApprovedProduct
        fields = ('discount', 'user', 'pickup_address', 'images', 'title', 'description', 'style', 'brand', 'original_price',
                  'listing_price', 'occasion', 'product_category', 'color', 'age', 'condition', 'sale', 'size_type', 'completed')


class AndroidProductsToApproveSerializer(serializers.ModelSerializer):
    # title = serializers.CharField()
    # description = serializers.CharField()

    class Meta:
        model = ApprovedProduct
        fields = ('user', 'title', 'description', 'style', 'brand', 'occasion', 'product_category', 'color',
                  'sale', 'original_price', 'listing_price', 'age', 'condition', 'size_type', 'pickup_address', 'completed')


class NumberOfProductSrlzr(serializers.ModelSerializer):

    class Meta:
        model = NumberOfProducts
        fields = ('size', 'product', 'quantity', 'time_to_make', 'alternate_size')


class SingleApprovedProducSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    condition = serializers.SerializerMethodField()
    commentCount = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    occasion = serializers.SerializerMethodField()
    admire_or_not = serializers.SerializerMethodField()
    available_size = serializers.SerializerMethodField()
    sub_cat = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()

    def get_shop(self, foo):
        if foo.shop == 1:
            return "designer"
        elif foo.shop == 2:
            return "curated"
        elif foo.shop == 3:
            return "market"
        elif foo.shop == 4:
            return "brand"
        else:
            return None

    def get_title(self, obj):
        return ((obj.color.name + ' ') if obj.color else (obj.style.style_type + ' ') if obj.style else '') + obj.product_category.name if obj.user.user_type.name not in ['designer', 'zap_exclusive'] else obj.title

    def get_user(self, obj):
        # if obj.user.user_type.name in ['zap_exclusive']:
        #     user_data = {'id': str(obj.user.id), 'user_type': str(obj.user.user_type.name)}
        #     return user_data
        if obj.user.user_type.name in ['zap_exclusive']:
            return None
        return UserSerializer(obj.user).data

    def get_likes(self, obj):
        logged_user = self.context['current_user']
        all_likes = [{'id':u.id,'zap_username':u.zap_username} for u in obj.loves.all()]
        # likes = list(all_likes)
        me = []
        liker1 = []
        others = []
        if not (logged_user.is_anonymous() or logged_user.is_superuser):
            admirings = [{'id':u.user.id,'zap_username':u.user.zap_username} for u in UserProfile.objects.filter(admiring__in=[logged_user.profile.user.id])]
            if logged_user in obj.loves.all():
                me = [{'id':logged_user.id,'zap_username':logged_user.zap_username}]
                all_likes.remove(me[0])
            liker1 = [x for x in admirings if x in all_likes]
        others = [x for x in all_likes if x not in liker1]
        return {'me':me, 'liker1':liker1, 'others':others}

    def get_commentCount(self, obj):
        return obj.comments_got.count()

    def get_style(self, obj):
        return obj.style.style_type if obj.style else None

    def get_color(self, obj):
        return obj.color.name if obj.color else None

    def get_product_category(self, obj):
        return {'name':obj.product_category.parent.name,'id':obj.product_category.parent.slug}

    def get_sub_cat(self, obj):
        return obj.product_category.id

    def get_occasion(self, obj):
        return {'id':obj.occasion.id,'name':obj.occasion.name} if obj.occasion else None

    def get_available_size(self, foo):
        return [{'size_id': product.size.id, 'quantity': product.quantity} for product in foo.product_count.filter(quantity__gt=0)]

    def get_brand(self, obj):
        return {'id':obj.brand.slug,'name':obj.brand.brand}

    def get_condition(self, obj):
        return obj.get_condition_display()

    def get_admire_or_not(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.user.profile.admiring.all():
                return True
            else:
                return False
        else:
            return False


    class Meta:
        model = ApprovedProduct
        fields = ('id', 'shop', 'title', 'user','likes','commentCount','style','occasion','color','product_category',
                  'admire_or_not','available_size', 'best_price', 'time_to_make','listing_price','original_price',
                  'sub_cat','brand','condition')


class AndroidSingleApprovedProducSerializer(serializers.ModelSerializer):
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
    shop = serializers.SerializerMethodField()

    def get_shop(self, foo):
        if foo.shop == 1:
            return "designer"
        elif foo.shop == 2:
            return "curated"
        elif foo.shop == 3:
            return "market"
        elif foo.shop == 4:
            return "brand"
        else:
            return None

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

    def get_flash_sale_data(self, obj):
        data = obj.get_flash_sale_data()
        if data:
            from zap_apps.marketing.models import CampaignProducts
            campaign_products = CampaignProducts.objects.filter(products=obj.id,
                                                                campaign__offer__start_time__lt=timezone.now(),
                                                                campaign__offer__end_time__gt=timezone.now(),
                                                                campaign__offer__status=True)
            campaign_product = campaign_products[0]
            offer = campaign_product.campaign.offer
            timediff = offer.end_time.replace(tzinfo=None) - datetime.datetime.now().replace(tzinfo=None)
            data = {'extra_discount':str(int(campaign_product.discount)), 'sale_name': offer.name,
                    'show_timer': offer.show_timer, 'end_timestamp': timediff.total_seconds(),
                    'end_time': timediff.days * 86400 + timediff.seconds, 'before_flash_sale_price': obj.listing_price}
        return data

    class Meta:
        model = ApprovedProduct
        fields = ('title', 'shipping_charge', 'num_products_of_user', 'no_of_products',
            'size', 'id', 'user', 'title', 'description', 'commentCount', 'likesCount',
            'liked_by_user', 'images', 'size_type', 'sale', 'product_category',
            'original_price', 'listing_price', 'discount', 'upload_time', 'style',
            'brand', 'occasion', 'color', 'age', 'condition', 'admired_by_user',
            'sold_out', 'available', 'deletable', 'best_price', 'time_to_make', 'flash_sale_data', 'shop')


class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('user_commented')

    def user_commented(self, foo):
        return UserSerializer(foo.commented_by).data

    class Meta:
        model = Comments
        fields = ('id', 'comment', 'user')


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('profile_picture')
    product_images = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    admires_count = serializers.SerializerMethodField()
    outfit_count = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    seller_type = serializers.SerializerMethodField()

    def get_user_type(self, obj):
        return obj.user_type.name

    def get_product_images(self, obj):
        return [{'url': i.images.all().order_by('id')[0].image.url_500x500 if i.images.all() else "", 'id':i.id,'title':i.title,'original_price':i.original_price,'listing_price':i.listing_price} for i in ApprovedProduct.ap_objects.filter(user=obj)[0:4]]

    def profile_picture(self, obj):
        return obj.profile.profile_pic

    def get_admires_count(self, obj):
        return obj.profile.admiring.count()

    def get_outfit_count(self, obj):
        return ApprovedProduct.ap_objects.filter(user=obj).count()

    def get_fullname(self, obj):
        return obj.first_name+' '+obj.last_name

    def get_description(self, obj):
        return obj.profile.description

    def get_seller_type(self, obj):
        if obj.user_type.name == 'designer' and hasattr(obj, 'representing_brand'):
            if obj.representing_brand.designer_brand:
                data = {'name':'Indian Brands', 'slug':'designer'}
                return data
            else:
                data = {'name': 'International Brands', 'slug': 'brand'}
                return data
        elif obj.user_type.name == 'zap_exclusive':
            data = {'name': 'Curated By Zapyle', 'slug': 'curated'}
            return data
        else:
            data = {'name': 'Marketplace', 'slug': 'market'}
            return data

    class Meta:
        model = ZapUser
        fields = ('id', 'zap_username', 'profile_pic', 'product_images','user_type','admires_count', 'outfit_count','fullname','description','seller_type')


class UserSerializer2(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('profile_picture')

    def profile_picture(self, foo):
        return foo.profile.profile_pic

    class Meta:
        model = ZapUser
        fields = ('id', 'zap_username', 'profile_pic')


class AndroidUserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('profile_picture')
    user_type = serializers.SerializerMethodField()

    def get_user_type(self, foo):
        return foo.user_type.name

    def profile_picture(self, foo):
        return foo.profile.profile_pic

    class Meta:
        model = ZapUser
        fields = ('id', 'zap_username', 'profile_pic', 'user_type')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = ('id', 'product', 'commented_by', 'comment', 'comment_time')


class GetDataCommentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class GetCommentSerializer(serializers.ModelSerializer):
    commented_by = serializers.SerializerMethodField('get_product_comments')
    comment_time = serializers.SerializerMethodField(
        'get_product_commented_time')
    mentioned_users = serializers.SerializerMethodField()

    def get_product_commented_time(self, foo):
        return timesince.timesince(foo.comment_time) + " ago."

    def get_product_comments(self, foo):
        return {'id': foo.commented_by.id, 'profile_pic': foo.commented_by.profile.profile_pic, 'zap_username': foo.commented_by.zap_username}

    def get_mentioned_users(self, foo):
        all_word_list = re.findall(r'[@]\w+', foo.comment)
        mentioned_list = []
        for current in all_word_list:
            user = ZapUser.objects.filter(zap_username=current[1:])
            if user:
                mentioned_list.append(
                    (foo.comment.find(current), len(current), user[0].id))
        return mentioned_list

    class Meta:
        model = Comments
        fields = (
            'id', 'commented_by', 'comment', 'comment_time', 'mentioned_users')

class GetCommentSerializerWeb(serializers.ModelSerializer):
    commented_by = serializers.SerializerMethodField('get_product_comments')
    comment_time = serializers.SerializerMethodField(
        'get_product_commented_time')
    comment = serializers.SerializerMethodField()

    def get_product_commented_time(self, foo):
        return timesince.timesince(foo.comment_time) + " ago."

    def get_product_comments(self, foo):
        return {'id': foo.commented_by.id,
            'profile_pic': foo.commented_by.profile.profile_pic,
            'zap_username': foo.commented_by.zap_username or foo.commented_by.get_full_name(),
            'full_name': foo.commented_by.get_full_name() or foo.commented_by.zap_username
            }

    def get_comment(self, foo):
        for i in ZapUser.objects.filter(zap_username__in=[s.replace('@', '') for s in re.findall('@\w+', foo.comment)]):
            foo.comment = foo.comment.replace("@"+i.zap_username, '<a href="{}/profile/{}/{}">@{}</a>'.format(settings.CURRENT_DOMAIN,i.id,i.zap_username,i.zap_username))

        return foo.comment

    class Meta:
        model = Comments
        fields = ('id', 'commented_by', 'comment', 'comment_time')


class GetLikeSerializer(serializers.ModelSerializer):
    loved_by = serializers.SerializerMethodField('get_product_likes')

    def get_product_likes(self, foo):
        return {'id': foo.loved_by.id, 'profile_pic': foo.loved_by.profile.profile_pic, 'zap_username': foo.loved_by.zap_username or foo.loved_by.get_full_name()}

    class Meta:
        model = Loves
        fields = ('loved_by', 'id')


class GetLikeSerializerWeb(serializers.ModelSerializer):
    loved_by = serializers.SerializerMethodField('get_product_likes')

    def get_product_likes(self, foo):
        logged_user = self.context['current_user']
        if not logged_user.is_anonymous():
            if logged_user in foo.loved_by.profile.admiring.all():
                status = True
            else:
                status = False
        else:
            status = False
        return {
            'id': foo.loved_by.id,
            'profile_pic': foo.loved_by.profile.profile_pic,
            'zap_username': foo.loved_by.zap_username or foo.loved_by.get_full_name(),
            'full_name' : foo.loved_by.get_full_name() or foo.loved_by.zap_username,
            'admire_or_not' : status
        }

    class Meta:
        model = Loves
        fields = ('loved_by', 'id')

class ZapUserProductsSerializer(serializers.ModelSerializer):
    num_of_products = serializers.SerializerMethodField('get_product_count')
    profile_pic = serializers.SerializerMethodField('profile_picture')
    products = serializers.SerializerMethodField('get_product_details')
    admires_count = serializers.SerializerMethodField()
    admire_or_not = serializers.SerializerMethodField()

    def get_admires_count(self, foo):
        return foo.profile.admiring.count()

    def get_product_count(self, foo):
        return foo.approved_product(manager='ap_objects').count()

    def profile_picture(self, foo):
        return foo.profile.profile_pic

    def get_product_details(self, foo):
        return [{'id': p.id, 'image': p.images.all().order_by('id')[0].image.url_100x100} for p in foo.approved_product(manager='ap_objects').all()[:settings.CATALOGUE_SELLERVIEW_LINE_ITEM_COUNT]]
        # return ApprovedProductSerializer(foo.approved_product.filter(sale='2')[:settings.CATALOGUE_SELLERVIEW_LINE_ITEM_COUNT],many=True,
        # context={'logged_user': self.context['current_user']}).data

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
        depth = 1
        fields = ('id', 'zap_username', 'profile_pic', 'num_of_products',
                  'products', 'admires_count', 'admire_or_not')


class ApprovedProductSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField('get_comments_count')
    likes_count = serializers.SerializerMethodField('number_of_likes')
    liked_by_user = serializers.SerializerMethodField('liked_by_users')
    user = serializers.SerializerMethodField('get_product_user_type')
    sale = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField("get_number_of_products")
    size = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    offer = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.get_title()
    def get_offer(self, obj):
        return obj.get_flash_sale_data()
    def get_images(self, obj):
        return [{'id': i.id, 'image': i.image.url_500x500} for i in obj.images.all().order_by('id')]

    def get_discount(self, obj):
        if obj.sale == '2' and not obj.discount:
            return None

        if obj.discount != '' and obj.discount != None and obj.discount != 0:
            return str(int(obj.discount*100))+'% off' if obj.sale=='2' else 'Inspiration'
        else:
            return None

    def get_size(self, obj):
        # import pdb; pdb.set_trace()
        size = ''
        if obj.size_type == 'FREESIZE':
            if obj.product_count.get(size__category_type="FS").quantity > 0:
                size = 'FREESIZE'
        else:
            s_type = obj.size_type
            for s in obj.size.all().extra(select={'i': 'CAST(uk_size AS FLOAT)'}).order_by('i'):
                if obj.product_count.get(size=s).quantity > 0:
                    size += str(s_type) + \
                        (str(s.uk_size) if str(s_type) == 'UK' else str(s.us_size) if str(s_type) ==
                         'US' else str(s.eu_size))+' '
        return size

    def get_sale(self, obj):
        return obj.get_sale_display()

    def get_product_user_type(self, foo):
        return {'user_type': foo.user.user_type.name, 'user_id': foo.user.id}

    def get_comments_count(self, foo):
        return foo.comments_got.count()

    def number_of_likes(self, foo):
        return foo.likes_got.count()

    def liked_by_users(self, foo):
        logged_user = self.context['logged_user']
        if not logged_user.is_anonymous():
            return True if logged_user in foo.loves.all() else False
        else:
            return False

    def get_number_of_products(self, foo):
        return True if foo.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else False
    def get_category(self, foo):
        return foo.product_category.parent.name

    class Meta:
        model = ApprovedProduct
        depth = 1
        fields = ('user', 'id', 'title', 'images', 'original_price', 'discount', 'listing_price', 'sale',
                  'style', 'likes_count', 'comment_count', 'brand', 'liked_by_user', 'available', 'size_type', 'size', 'category', 'offer')


class UpdateApprovedProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApprovedProduct
        exclude = ('user', 'seller_recommendations')


class ApprovedProductSerializerAndroid(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField('get_comments_count')
    likes_count = serializers.SerializerMethodField('number_of_likes')
    liked_by_user = serializers.SerializerMethodField('liked_by_users')
    uploaded_by = serializers.SerializerMethodField('uploaded_user')
    sale = serializers.SerializerMethodField('get_sale_status')
    images = serializers.SerializerMethodField('get_product_images')
    brand = serializers.SerializerMethodField('get_product_brand')
    available = serializers.SerializerMethodField("get_number_of_products")
    sold_out = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    size_type = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    offer = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            'user_id':obj.user.id,
            'user_type':obj.user.user_type.name
        }

    def get_title(self, obj):
        return obj.get_title()
    def get_offer(self, obj):
        return obj.get_flash_sale_data()
    def get_size_type(self, foo):
        return foo.size_type or (
            "UK" if foo.product_category.parent.category_type == 'C' else
            "US" if foo.product_category.parent.category_type == 'FW' else "FREESIZE")

    def get_discount(self, foo):
        if foo.discount != '' and foo.discount != None and foo.discount != 0:
            return int(foo.discount*100) if foo.discount else None
        return None

    def get_style(self, foo):
        return foo.style.style_type if foo.style else None

    def get_number_of_products(self, foo):
        return True if foo.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else False

    def get_comments_count(self, foo):
        return foo.comments_got.count()

    def number_of_likes(self, foo):
        return foo.likes_got.count()

    def liked_by_users(self, foo):
        logged_user = self.context['logged_user']
        if not logged_user.is_anonymous():
            return True if logged_user in foo.loves.all() else False
        else:
            return False

    def get_sale_status(self, foo):
        return foo.get_sale_display()

    def get_product_images(self, foo):
        return [i.image.url_500x500 for i in foo.images.all().order_by('id')[:1]]

    def get_product_brand(self, foo):
        return foo.brand.brand

    def uploaded_user(self, foo):
        # return foo.user.id
        return {
            'id': foo.user.id,
            'zap_username': foo.user.zap_username,
            'profile_pic': foo.user.profile.profile_pic,
            'user_type': foo.user.user_type.name}

    def get_sold_out(self, foo):
        return False if foo.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else True

    class Meta:
        model = ApprovedProduct
        depth = 1
        fields = ('uploaded_by', 'id', 'title', 'images', 'original_price', 'discount', 'listing_price', 'sale', 'user',
                  'style', 'likes_count', 'comment_count', 'brand', 'liked_by_user', 'available', 'size_type', 'sold_out', 'offer')


class EditProducSerializer(serializers.ModelSerializer):
    # commentCount = serializers.SerializerMethodField('get_comments_count')
    # likesCount = serializers.SerializerMethodField('get_likes_count')
    # liked_by_user = serializers.SerializerMethodField('liked_by_users')
    # comments = serializers.SerializerMethodField('get_full_comments')
    # user = serializers.SerializerMethodField('user_details')
    # no_of_products = serializers.SerializerMethodField('get_products_count')
    # num_products_of_user = serializers.SerializerMethodField('get_user_num_products')
    # age = serializers.SerializerMethodField()
    # condition = serializers.SerializerMethodField()

    # def get_age(self,obj):
    #     return obj.get_age_display()
    # def get_condition(self,obj):
    #     return obj.get_condition_display()
    # def get_comments_count(self,foo):
    #     return foo.comments_got.count()
    # def get_likes_count(self,foo):
    #     return foo.likes_got.count()
    # def liked_by_users(self,foo):
    #     logged_user = self.context['current_user']
    #     if not logged_user.is_anonymous():
    #         return True if logged_user in foo.loves.all() else False
    #     else:
    #         return False
    # def get_full_comments(self,foo):
    #     srlzr = CommentsSerializer(foo.comments_got.all(), many=True)
    #     return srlzr.data
    # def user_details(self, foo):
    #     return UserSerializer(foo.user).data

    # def get_user_num_products(self, foo):
    #     return foo.user.approved_product.count()
    # def get_products_count(self, foo):
    # return [{'size_id':product.size.id,'quantity':product.quantity} for
    # product in foo.product_count.all()]
    no_of_products = serializers.SerializerMethodField('get_products_count')

    def get_products_count(self, foo):
        return [{'size': str(product.size.id), 'quantity': product.quantity, 'size_type': 'US'} for product in foo.product_count.all()]

    class Meta:
        model = ApprovedProduct
        depth = 1
        fields = ('id', 'pickup_address', 'images', 'title', 'description', 'style', 'brand', 'original_price', 'upload_time',
                  'sale', 'no_of_products', 'listing_price', 'occasion', 'product_category', 'color', 'completed', 'age', 'condition')
        #fields = ('num_products_of_user', 'no_of_products', 'size', 'id','user','title','description','commentCount','likesCount','liked_by_user','images','comments','sale','product_category','original_price','listing_price','discount','upload_time','style','brand','occasion','color','age','condition')


class GetApprovedProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApprovedProduct
        field = '__all__'


class Base64ImageField(serializers.ImageField):

    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            # 12 characters are more than enough.
            file_name = str(uuid.uuid4())[:12]
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class ProductImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = ProductImage
        field = ('id', 'image',)


class ConversationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversations
        field = ('id','comment','mentions')

class ZapCuratedEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ZapCuratedEntry
        fields = '__all__'


class SellerClosetViewSerializer(serializers.ModelSerializer):
    admiring = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    more_product = serializers.SerializerMethodField()
    total_more_product = serializers.SerializerMethodField()
    def get_admiring(self, foo):
        current_user_id = self.context['current_user_id']
        return current_user_id in foo.profile.admiring.all().values_list('id', flat=True)

    def get_product(self, foo):
        return [{'id': i.id, 'title': i.title, 'image': settings.CURRENT_DOMAIN + \
            i.images.all().order_by('id')[0].image.url_500x500} for i in \
            foo.approved_product.filter(status='1').annotate(sum_count=Sum('product_count__quantity')).exclude(images__isnull=True).order_by('-sum_count')[:5]]
    def get_more_product(self, foo):
        return [{'image': settings.CURRENT_DOMAIN + \
            i.images.all().order_by('id')[0].image.url_100x100} for i in \
            foo.approved_product.filter(status='1').annotate(sum_count=Sum('product_count__quantity')).exclude(images__isnull=True).order_by('-sum_count')[3:7]]
    def get_profile_pic(self, foo):
        return foo.profile.profile_pic_original
    def get_full_name(self, foo):
        return foo.get_full_name()
    def get_total_more_product(self, foo):
        return foo.approved_product.filter(status='1').annotate(sum_count=Sum('product_count__quantity')).exclude(images__isnull=True).order_by('-sum_count')[3:].count()

    class Meta:
        model = ZapUser
        fields = ('id', 'zap_username', 'admiring', 'product', 'profile_pic', 'full_name','more_product','total_more_product')


class ProductIndexSerializer(serializers.ModelSerializer):
    commentCount = serializers.SerializerMethodField('get_comments_count')
    likesCount = serializers.SerializerMethodField('get_likes_count')
    # comments = serializers.SerializerMethodField('get_full_comments')
    user = serializers.SerializerMethodField('user_details')
    no_of_products = serializers.SerializerMethodField('get_products_count')
    num_products_of_user = serializers.SerializerMethodField(
        'get_user_num_products')
    age = serializers.SerializerMethodField()
    age_id = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    condition = serializers.SerializerMethodField()
    condition_id = serializers.SerializerMethodField()
    product_parent_category = serializers.SerializerMethodField()
    product_parent_category_id = serializers.SerializerMethodField()
    product_parent_category_slug = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    product_category_id = serializers.SerializerMethodField()
    product_category_slug = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()
    style_slug = serializers.SerializerMethodField()
    style_id = serializers.SerializerMethodField()
    occasion = serializers.SerializerMethodField()
    occasion_slug = serializers.SerializerMethodField()
    occasion_id = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    color_slug = serializers.SerializerMethodField()
    color_id = serializers.SerializerMethodField()
    color_code = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    brand_slug = serializers.SerializerMethodField()
    brand_id = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    deletable = serializers.SerializerMethodField()
    size_type = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    shop_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    loves = serializers.SerializerMethodField()
    elastic_index = serializers.SerializerMethodField()

    def get_elastic_index(self, foo):
        return foo.elastic_index

    def get_loves(self, foo):
        return foo.loves.all().count()

    def get_status(self, foo):
        return foo.status

    def get_shop_id(self, foo):
        return foo.shop

    def get_shop(self, foo):
        if foo.shop == 1:
            return "designer"
        elif foo.shop == 2:
            return "curated"
        elif foo.shop == 3:
            return "market"
        elif foo.shop == 4:
            return "brand"
        else:
            return None

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

    def get_style_slug(self, foo):
        return foo.style.slug if foo.style else None

    def get_style_id(self, foo):
        return foo.style.id if foo.style else None

    def get_brand(self, foo):
        return foo.brand.brand if foo.brand else None

    def get_brand_id(self, foo):
        return foo.brand.id if foo.brand else None

    def get_brand_slug(self, foo):
        return foo.brand.slug if foo.brand else None

    def get_occasion(self, foo):
        return foo.occasion.name if foo.occasion else None

    def get_occasion_slug(self, foo):
        return foo.occasion.slug if foo.occasion else None

    def get_occasion_id(self, foo):
        return foo.occasion.id if foo.occasion else None

    def get_color(self, foo):
        return foo.color.name if foo.color else None

    def get_color_code(self, foo):
        return foo.color.code if foo.color else None

    def get_color_slug(self, foo):
        return foo.color.slug if foo.color else None

    def get_color_id(self, foo):
        return foo.color.id if foo.color else None

    def get_product_category(self, foo):
        return foo.product_category.name

    def get_product_category_id(self, foo):
        # print "product category " + str(foo.product_category.id)
        return foo.product_category.id

    def get_product_category_slug(self, foo):
        # print "product category " + str(foo.product_category.id)
        return foo.product_category.slug

    def get_product_parent_category(self, foo):
        return foo.product_category.parent.name

    def get_product_parent_category_id(self, foo):
        # print "product category " + str(foo.product_category.id)
        return foo.product_category.parent.id

    def get_product_parent_category_slug(self, foo):
        # print "product category " + str(foo.product_category.id)
        return foo.product_category.parent.slug

    def get_images(self, obj):
        return [i.image.url_1000x1000 for i in obj.images.all().order_by('id')]

    def get_age(self, obj):
        return obj.get_age_display()

    def get_age_id(self, obj):
        return obj.age

    def get_condition(self, obj):
        return obj.get_condition_display()

    def get_condition_id(self, obj):
        return obj.condition

    def get_comments_count(self, foo):
        return foo.comments_got.count()

    def get_likes_count(self, foo):
        return foo.likes_got.count()

    # def get_full_comments(self, foo):
    #     srlzr = CommentsSerializer(foo.comments_got.all(), many=True)
    #     return srlzr.data

    def user_details(self, foo):
        return AndroidUserSerializer(foo.user).data

    def get_user_num_products(self, foo):
        return foo.user.approved_product(manager='ap_objects').count()

    def get_products_count(self, foo):
        return [{'size_id': product.size.id, 'quantity': product.quantity} for product in foo.product_count.all()]

    sold_out = serializers.SerializerMethodField()

    def get_sold_out(self, foo):
        return False if foo.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] > 0 else True
    shipping_charge = serializers.SerializerMethodField()

    def get_shipping_charge(self, foo):
        return settings.SHIPPING_CHARGE if foo.listing_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0

    class Meta:
        model = ApprovedProduct
        fields = ('shipping_charge', 'num_products_of_user', 'no_of_products', 'loves', 'elastic_index',
            'size', 'id', 'user', 'title', 'description', 'commentCount', 'likesCount', 'product_category_slug',
            'images', 'size_type', 'sale', 'product_category', 'product_category_id', 'product_parent_category',
            'product_parent_category_id', 'product_parent_category_slug', 'color_slug', 'occasion_slug', 'style_slug',
            'original_price', 'listing_price', 'discount', 'upload_time', 'style', 'style_id', 'brand_slug',
            'brand', 'brand_id', 'occasion', 'occasion_id', 'color', 'color_id', 'age', 'age_id', 'condition', 'condition_id',
            'sold_out', 'available', 'deletable', 'best_price', 'time_to_make', 'shop_id', 'shop', 'color_code', 'status')


class LookProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    loved_by_user = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.images.all().order_by('id')[0].image.url_500x500

    def get_available(self, obj):
        return False if obj.product_count.all().aggregate(Sum('quantity'))[
                            'quantity__sum'] <= 0 or obj.sale == '1' else True

    def get_discount(self, obj):
        return int(obj.discount*100)

    def get_brand_name(self, obj):
        return obj.brand.brand

    def get_sizes(self, obj):
        return [{'id': s.id, 'size': s.size, 'uk_size': s.uk_size, 'us_size': s.us_size, 'eu_size': s.eu_size,
                 'category_type': s.category_type, 'quantity': obj.product_count.get(size=s).quantity} for s in
                obj.size.filter(sized_products__quantity__gt=0).extra(select={'i': 'CAST(uk_size AS FLOAT)'}).order_by('i')]

    def get_loved_by_user(self, foo):
        if 'user' in self.context:
            logged_user = self.context['user']
            if not logged_user.is_anonymous():
                return True if logged_user in foo.loves.all() else False
        else:
            return False

    class Meta:
        model = ApprovedProduct
        fields = ['id', 'title', 'image', 'brand', 'product_category', 'available', 'listing_price', 'original_price',
                  'discount', 'sizes', 'brand_name', 'loved_by_user']

