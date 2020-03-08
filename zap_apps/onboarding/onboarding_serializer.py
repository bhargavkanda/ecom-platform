from rest_framework import serializers
from zap_apps.zapuser.models import ZapUser, UserPreference
from rest_framework.validators import UniqueValidator
from zap_apps.account.account_serializer import check_phone_number
from zap_apps.zap_catalogue.models import Category, SubCategory
import re
from django.conf import settings
from zap_apps.zap_commons.common_serializers import ZapErrorModelSrlzr

class OnboardingSerializerStepOne(ZapErrorModelSrlzr):
    email = serializers.EmailField(max_length=254, validators=[
                                   UniqueValidator(queryset=ZapUser.objects.all(), message="Email already exists.")],
                                   error_messages=settings.ZAPERROR.error_messages.email.__dict__)
    zap_username = serializers.CharField(min_length=4, max_length=50, validators=[
                                         UniqueValidator(queryset=ZapUser.objects.all(), message="Username already exists.")],
                                         error_messages=settings.ZAPERROR.error_messages.zap_username.__dict__)
    phone_number = serializers.CharField(
        validators=[UniqueValidator(
            queryset=ZapUser.objects.all(), 
            message="Phone number already exists."
            )],error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)

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
            raise serializers.ValidationError("Mobile number is not valid.")
        return data

    class Meta:
        model = ZapUser
        fields = ('email', 'zap_username', 'phone_number')


class OnboardingSerializerStepTwo(serializers.ModelSerializer):
    pass


class OnboardingSerializerStepFour(serializers.ModelSerializer):

    class Meta:
        model = UserPreference
        fields = ('waist_size', 'size', 'foot_size')


class OnboardingStartEndSrlsr(serializers.Serializer):
    start = serializers.IntegerField(required=False)
    end = serializers.IntegerField(required=False)


class CategorySeriaizer(serializers.ModelSerializer):
    sub_cats = serializers.SerializerMethodField('get_sub_categories')

    def get_sub_categories(self, foo):
        return SubCategorySerializer(foo.subcategory_set.all(), many=True).data

    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type', 'sub_cats')


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = ('id', 'name')
# class OnboardingSerializerStepTwo(serializers.ModelSerializer):
#     class Meta:
#         model = UserPreference
#         fields = ('fashion_type',)

# class OnboardingSerializerStepTwo(serializers.ModelSerializer):
#     class Meta:
#         model = UserPreference
#         fields = ('fashion_type',)
