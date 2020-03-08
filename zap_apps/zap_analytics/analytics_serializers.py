from rest_framework import serializers

from zap_apps.zap_analytics.models import *
import pdb


class ProductAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductAnalytics
        field = '__all__'


class ProfileAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileAnalytics
        field = '__all__'


class SortAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SortAnalytics
        field = '__all__'


class SearchAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchAnalytics
        field = '__all__'


class FilterAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilterAnalytics
        field = '__all__'


class NotificationAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationAnalytics
        field = '__all__'


class ImpressionAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImpressionAnalytics
        field = '__all__'


class UserActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAction
        field = '__all__'

class AnalyticsSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnalyticsSessions
        field = '__all__'

class AnalyticsEventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnalyticsEvents
        field = '__all__'

class SellerAnalyticsByUserSerializer(serializers.ModelSerializer):

    analytics = serializers.SerializerMethodField()

    def get_analytics(self, obj):

        #pdb.set_trace()

        for product in obj:
            product_view_object = ProductAnalytics.objects.filter(product=product.id)
            product_impression_object = ImpressionAnalytics.objects.filter(product=product.id)

            data = {
            'total_views': product_view_object.count(),
            'unique_views' : product_view_object.order_by('user').distinct().count(),
            'total_impressions': product_impression_object.count(),
            'unique_impressions': product_impression_object.order_by('user').distinct().count()
            }

        import json
        return json.dumps(data)

    class Meta:
        model = ProductAnalytics
        field = ('analytics')