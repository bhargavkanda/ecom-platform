from rest_framework import serializers
from zap_apps.zapuser.models import ZapUser
from rest_framework.validators import UniqueValidator
import re
from django.conf import settings
from zap_apps.account.models import Testimonial
from zap_apps.zap_commons.common_serializers import ZapErrorModelSrlzr, ZapErrorSrlzr


def check_phone_number(num):
    return bool(re.match(r'^(\+91|0091|0[\-\s]?)?\d{10}$', str(num)))


class AccestokenSerializar(serializers.Serializer):
    access_token = serializers.CharField(max_length=1000)


class LoggedFromSerializar(serializers.Serializer):
    logged_from = serializers.CharField(max_length=15)
    logged_device = serializers.CharField()
    gcm_reg_id = serializers.CharField(required=False, min_length=3)

    def validate_logged_device(self, data):
        if data not in ["website", 'ios', 'android']:
            raise serializers.ValidationError(
                "logged_device should be website/ios/android.")
        return data

    def validate_logged_from(self, data):
        if not data in ["fb", "instagram", "zapyle"]:
            raise serializers.ValidationError(
                "logged_from should be fb/zapyle/instagram")
        return data

    def validate(self, data):
        if data['logged_device'] in ["ios", "android"]:
            if not data.get('gcm_reg_id'):
                raise serializers.ValidationError(
                    {"gcm_reg_id": "gcm_reg_id is required"})
        return data


class FbUserSlzr(serializers.Serializer):
    id = serializers.CharField(max_length=30)


class InstagramUserSlzr(serializers.Serializer):
    id = serializers.CharField(max_length=30)


class ResetPasswordSrlzr(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=30)


class OTPResetPasswordSrlzr(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=30)
    otp = serializers.CharField(required=True)
    confirm_password = serializers.CharField(min_length=6, max_length=30)
    # phone_number = serializers.CharField(min_length=10, max_length=14)
    logged_device = serializers.CharField(required=True)
    gcm_reg_id = serializers.CharField(required=False, min_length=3)

    def validate_logged_device(self, data):
        if data not in ["website", 'ios', 'android']:
            raise serializers.ValidationError("logged_device should be website/ios/android.")
        return data

    # def validate_phone_number(self, data):
    #     if not check_phone_number(data):
    #         raise serializers.ValidationError("Invalid mobile number.")
    #     return data

    def validate(self, data):
        if not data['password'] == data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "The passwords do not match"})
        if data['logged_device'] in ["ios", "android"]:
            if not data.get('gcm_reg_id'):
                raise serializers.ValidationError(
                    {"gcm_reg_id": "gcm_reg_id is required"})
        return data


class ZapLoginUserSlzr(serializers.Serializer):
    email = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=30)


class ZapEmailSlzr(serializers.Serializer):
    email = serializers.EmailField(max_length=30)


class ZapSignupUserSlzr(ZapErrorSrlzr):

    email = serializers.EmailField(min_length=10, max_length=30, validators=[UniqueValidator(
        queryset=ZapUser.objects.all(), message=settings.ZAPERROR.error_messages.email.unique)], error_messages=settings.ZAPERROR.error_messages.email.__dict__)
    zap_username = serializers.CharField(min_length=4, max_length=30, validators=[UniqueValidator(
        queryset=ZapUser.objects.all(), message=settings.ZAPERROR.error_messages.zap_username.unique)], error_messages=settings.ZAPERROR.error_messages.zap_username.__dict__)
    first_name = serializers.CharField(max_length=30, error_messages=settings.ZAPERROR.error_messages.first_name.__dict__)
    last_name = serializers.CharField(max_length=30, default="")
    password = serializers.CharField(min_length=6, max_length=30, error_messages=settings.ZAPERROR.error_messages.password.__dict__)
    phone_number = serializers.CharField(min_length=10, max_length=14, validators=[UniqueValidator(
        queryset=ZapUser.objects.all(), message=settings.ZAPERROR.error_messages.phone_number.unique)], error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)
    confirm_password = serializers.CharField(min_length=6, max_length=30, error_messages=settings.ZAPERROR.error_messages.confirm_password.__dict__)
    logged_device = serializers.CharField(required=True)
    gcm_reg_id = serializers.CharField(required=False, min_length=3)

    def validate_zap_username(self, data):
        if not re.match("^[a-zA-Z0-9_]+$", data):
            raise serializers.ValidationError(
                "Username can contain only alphabets, numbers and '_'")
        if re.match("^[0-9]+$", data):
            raise serializers.ValidationError(
                "Username must contain at least one alphabet.")
        return data

    def validate_logged_device(self, data):
        if data not in ["website", 'ios', 'android']:
            raise serializers.ValidationError(
                "logged_device should be website/ios/android.")
        return data

    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Invalid phone number.")
        return data

    def validate(self, data):
        if not data['password'] == data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "The passwords do not match."})
        if data['logged_device'] in ["ios", "android"]:
            if not data.get('gcm_reg_id'):
                raise serializers.ValidationError(
                    {"gcm_reg_id": "gcm_reg_id is required"})
        return data

class ZapReducedSignupUserSlzr(ZapErrorSrlzr):
    email = serializers.EmailField(min_length=10, max_length=30, validators=[UniqueValidator(
        queryset=ZapUser.objects.all(), message=settings.ZAPERROR.error_messages.email.unique)], error_messages=settings.ZAPERROR.error_messages.email.__dict__)
    zap_username = serializers.CharField(min_length=4, max_length=30, validators=[UniqueValidator(
        queryset=ZapUser.objects.all(), message=settings.ZAPERROR.error_messages.zap_username.unique)], error_messages=settings.ZAPERROR.error_messages.zap_username.__dict__)
    full_name = serializers.CharField(max_length=60, error_messages=settings.ZAPERROR.error_messages.name.__dict__)
    password = serializers.CharField(min_length=6, max_length=30, error_messages=settings.ZAPERROR.error_messages.password.__dict__)
    phone_number = serializers.CharField(min_length=10, max_length=14, validators=[UniqueValidator(
        queryset=ZapUser.objects.all(), message=settings.ZAPERROR.error_messages.phone_number.unique)], error_messages=settings.ZAPERROR.error_messages.phone_number.__dict__)
    logged_device = serializers.CharField(required=True)
    gcm_reg_id = serializers.CharField(required=False, min_length=3)
    sex = serializers.CharField(required=False, max_length=10)

    def validate_zap_username(self, data):
        if not re.match("^[a-zA-Z0-9_]+$", data):
            raise serializers.ValidationError(
                "Username can contain only alphabets, numbers and '_'")
        if re.match("^[0-9]+$", data):
            raise serializers.ValidationError(
                "Username must contain at least one alphabet.")
        return data

    def validate_logged_device(self, data):
        if data not in ["website", 'ios', 'android']:
            raise serializers.ValidationError(
                "logged_device should be website/ios/android.")
        return data

    def validate_phone_number(self, data):
        if not check_phone_number(data):
            raise serializers.ValidationError(
                "Invalid phone number.")
        return data

    def validate(self, data):
        if data['logged_device'] in ["ios", "android"]:
            if not data.get('gcm_reg_id'):
                raise serializers.ValidationError(
                    {"gcm_reg_id": "gcm_reg_id is required"})
        return data

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ('text', 'user', 'location')
