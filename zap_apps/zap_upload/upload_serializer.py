from rest_framework import serializers
from zap_apps.zap_catalogue.models import ApprovedProduct, SubCategory, AGE, CONDITIONS
from zap_apps.address.models import Address
from zap_apps.zapuser.models import UserProfile
from zap_apps.zap_catalogue.product_serializer import Base64ImageField


class ProPicSrlzr(serializers.ModelSerializer):
    pro_pic = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = UserProfile
        field = ('pro_pic',)

class GetApprovedProductStep1(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField('get_brand_id_name')
    style = serializers.SerializerMethodField('get_style_id_name')
    color = serializers.SerializerMethodField('get_color_id_name')
    occasion = serializers.SerializerMethodField('get_occasion_id_name')
    images = serializers.SerializerMethodField('get_product_images')
    size = serializers.SerializerMethodField('get_product_sizes')
    product_category = serializers.SerializerMethodField(
        'get_product_category_id_name')

    def get_brand_id_name(self, foo):
        return {'id': foo.brand.id, 'name': foo.brand.brand}

    def get_style_id_name(self, foo):
        return {'id': foo.style.id, 'name': foo.style.style_type} if foo.style else None

    def get_color_id_name(self, foo):
        return {'id': foo.color.id, 'name': foo.color.name} if foo.color else None

    def get_occasion_id_name(self, foo):
        return {'id': foo.occasion.id, 'name': foo.occasion.name} if foo.occasion else None

    def get_product_images(self, foo):
        return [{'id': img.id, 'url': img.image.url_100x100} for img in foo.images.all()]

    def get_product_sizes(self, foo):
        size_type = foo.size_type
        return [{'id': s.size.id, 'size_type': size_type, 'uk_size': s.size.uk_size, 'us_size': s.size.us_size, 'eu_size': s.size.eu_size, 'category_type': s.size.category_type,'quantity':s.quantity} for s in foo.product_count.all()]
        #return [{'id': s.id, 'size_type': size_type, 'uk_size': s.uk_size, 'us_size': s.us_size, 'eu_size': s.eu_size, 'category_type': s.category_type} for s in foo.size.all()]

    def get_product_category_id_name(self, foo):
        return {'id': foo.product_category.id, 'name': foo.product_category.name}

    class Meta:
        model = ApprovedProduct
        fields = ('title', 'description', 'brand', 'style', 'color',
                  'images', 'occasion', 'sale', 'product_category', 'size')

class GetApprovedProductStep2(serializers.ModelSerializer):
    age = serializers.SerializerMethodField('get_age_name')
    condition = serializers.SerializerMethodField('get_condition_name')

    def get_age_name(self, foo):
        return foo.get_age_display()

    def get_condition_name(self, foo):
        return foo.get_condition_display()

    class Meta:
        model = ApprovedProduct
        fields = ('original_price', 'listing_price', 'age', 'condition')

class GetPTAStep1(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField('get_brand_id_name')
    style = serializers.SerializerMethodField('get_style_id_name')
    color = serializers.SerializerMethodField('get_color_id_name')
    occasion = serializers.SerializerMethodField('get_occasion_id_name')
    images = serializers.SerializerMethodField('get_product_images')
    size = serializers.SerializerMethodField('get_product_sizes')
    product_category = serializers.SerializerMethodField(
        'get_product_category_id_name')

    def get_brand_id_name(self, foo):
        return {'id': foo.brand.id, 'name': foo.brand.brand}

    def get_style_id_name(self, foo):
        return {'id': foo.style.id, 'name': foo.style.style_type}  if foo.style else None

    def get_color_id_name(self, foo):
        return {'id': foo.color.id, 'name': foo.color.name} if foo.color else None

    def get_occasion_id_name(self, foo):
        return {'id': foo.occasion.id, 'name': foo.occasion.name} if foo.occasion else None

    def get_product_images(self, foo):
        return [{'id': img.id, 'url': img.image.url_100x100} for img in foo.images.all()]

    def get_product_sizes(self, foo):
        size_type = foo.size_type
        return [{'id': s.size.id, 'size_type': size_type, 'uk_size': s.size.uk_size, 'us_size': s.size.us_size, 'eu_size': s.size.eu_size, 'category_type': s.size.category_type,'quantity':s.quantity} for s in foo.product_count.all()]
        # return [{'id': s.id, 'size_type': size_type, 'uk_size': s.uk_size, 'us_size': s.us_size, 'eu_size': s.eu_size, 'category_type': s.category_type} for s in foo.size.all()]

    def get_product_category_id_name(self, foo):
        return {'id': foo.product_category.id, 'name': foo.product_category.name}

    class Meta:
        model = ApprovedProduct
        fields = ('title', 'description', 'brand', 'style', 'color',
                  'images', 'occasion', 'sale', 'product_category', 'size')
class GetPTAStep2(serializers.ModelSerializer):
    age = serializers.SerializerMethodField('get_age_name')
    condition = serializers.SerializerMethodField('get_condition_name')

    def get_age_name(self, foo):
        return foo.get_age_display()

    def get_condition_name(self, foo):
        return foo.get_condition_display()

    class Meta:
        model = ApprovedProduct
        fields = ('original_price', 'listing_price', 'age', 'condition')
        
class GetPTAStep2PUT(serializers.ModelSerializer):
    age = serializers.ChoiceField(choices=AGE, required=True)
    condition = serializers.ChoiceField(choices=CONDITIONS, required=True)

    def get_age_name(self, foo):
        return foo.get_age_display()

    def get_condition_name(self, foo):
        return foo.get_condition_display()

    class Meta:
        model = ApprovedProduct
        fields = ('original_price', 'listing_price', 'age', 'condition')

class GetPTAStep3(serializers.ModelSerializer):
    class Meta:
        model = ApprovedProduct
        fields = ('pickup_address','completed')
  

class GetApprovedProductStep3(serializers.ModelSerializer):

    class Meta:
        model = ApprovedProduct
        fields = ('pickup_address',)


class UpdateApprovedProductSerializerAndroid(serializers.ModelSerializer):
    # images = serializers.PrimaryKeyRelatedField(many=True,required=False,read_only=True)
    seller_recommendations = serializers.PrimaryKeyRelatedField(
        many=True, required=False, read_only=True)
    user = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    class Meta:
        model = ApprovedProduct
        field = '__all__'

class UpdatePTASerializerAndroid(serializers.ModelSerializer):
    # images = serializers.PrimaryKeyRelatedField(many=True,required=False,read_only=True)
    user = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    class Meta:
        model = ApprovedProduct
        field = '__all__'

class StringListField(serializers.ListField):
    child = serializers.DictField()

class UploadPage1An(serializers.Serializer):
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    description = serializers.CharField(min_length=20, error_messages={'min_length': "Please enter at least 20 characters about your product :)."})

class UploadPage2An(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=ApprovedProduct.objects.all())


# class UploadPage3An(serializers.Serializer):
#     original_price = serializers.IntegerField()
#     listing_price = serializers.IntegerField()
#     def validate(self, data):
#         if data['listing_price'] > data['original_price']:
#             raise serializers.ValidationError({'listing_price': 'should be less than original_price'})
#         return data

class UploadPage3An(serializers.Serializer):
    original_price = serializers.IntegerField()
    listing_price = serializers.IntegerField()
    age = serializers.ChoiceField(choices=AGE, required=True)
    condition = serializers.ChoiceField(choices=CONDITIONS, required=True)
    def validate(self, data):
        if data['listing_price'] > data['original_price']:
            raise serializers.ValidationError({'listing_price': 'should be less than original_price'})
        return data

class UploadPage4An(serializers.Serializer):
    pickup_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())