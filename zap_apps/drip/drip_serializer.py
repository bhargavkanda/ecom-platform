from rest_framework import serializers
from zap_apps.zap_catalogue.models import ApprovedProduct, AGE, CONDITIONS
from zap_apps.address.models import Address
from zap_apps.zapuser.models import ZapUser
import pdb

def get_size_type(product):
    return product.size_type or (
        "UK" if product.product_category.parent.category_type == 'C' else
        "US" if product.product_category.parent.category_type == 'FW' else "FREESIZE")
def get_size_string(product):
    size_type = get_size_type(product)
    if size_type == "FREESIZE":
        return "FREESIZE"
    if size_type == "US":
        return ["US_{}".format(i.us_size) for i in product.size.all()]
    if size_type == "UK":
        return ["UK_{}".format(i.uk_size) for i in product.size.all()]
    if size_type == "EU":
        return ["EU_{}".format(i.eu_size) for i in product.size.all()]



class PickUpAddressSerializer(serializers.ModelSerializer):
	address = serializers.SerializerMethodField()
	state = serializers.SerializerMethodField()

	def get_address(self, foo):
		return "{0} {1}".format(foo.address,foo.address2)
	def get_state(self, foo):
		return foo.state.name

	class Meta:
		model = Address
		fields = ('name', 'address', 'city', 'state', 'country', 'phone', 'pincode')


class ContentProductSerializer(serializers.ModelSerializer):

	user = serializers.SerializerMethodField()
	loves = serializers.SerializerMethodField()
	pickup_address = serializers.SerializerMethodField()
	image = serializers.SerializerMethodField()
	brand = serializers.SerializerMethodField()
	style = serializers.SerializerMethodField()
	upload_time = serializers.SerializerMethodField()
	size = serializers.SerializerMethodField()
	occasion = serializers.SerializerMethodField()
	product_category = serializers.SerializerMethodField()
	color = serializers.SerializerMethodField()
	age = serializers.SerializerMethodField()
	condition = serializers.SerializerMethodField()

	def get_user(self, obj):
		return {'name':obj.user.get_full_name(), 'zap_username':obj.user.get_full_name()}
	def get_loves(self, obj):
		return {'count':obj.loves.count()}
	def get_pickup_address(self, obj):
		return PickUpAddressSerializer(obj.pickup_address).data
	def get_image(self, obj):
		return obj.images.all().order_by('id')[0].image.url_1000x1000
	def get_brand(self, obj):
		return obj.brand.brand
	def get_style(self, obj):
		return obj.style.style_type
	def get_upload_time(self, obj):
		return obj.upload_time.date().strftime('%d-%m-%Y')
	def get_size(self, obj):
		return get_size_string(obj)
	def get_occasion(self, obj):
		return obj.occasion.name
	def get_product_category(self, obj):
		return obj.product_category.name
	def get_color(self, obj):
		return obj.color.name
	def get_age(self, obj):
		age_dict = dict(AGE)
		return age_dict.get(obj.age, 'NA')
	def get_condition(self, obj):
		condition_dict = dict(CONDITIONS)
		return condition_dict.get(obj.condition, 'NA')



	class Meta:
		model = ApprovedProduct
		fields = ('user', 'loves', 'pickup_address', 'image', 'title', 'description',
			'brand', 'style', 'original_price', 'listing_price', 'upload_time', 'size',
			'occasion', 'product_category', 'color', 'age', 'condition', 'discount')

class ContentUserSerializer(serializers.ModelSerializer):
	name = serializers.SerializerMethodField()
	logged_device = serializers.SerializerMethodField()
	user_type = serializers.SerializerMethodField()
	available_zapcash = serializers.SerializerMethodField()

	def get_name(self, obj):
		return obj.get_full_name()
	def get_logged_device(self, obj):
		return obj.logged_device.name
	def get_user_type(self, obj):
		return obj.user_type.name
	def get_available_zapcash(self, obj):
		return obj.get_zap_wallet

	class Meta:
		model = ZapUser
		fields = ('name', 'zap_username', 'phone_number', 'logged_device', 'user_type', 'available_zapcash')







