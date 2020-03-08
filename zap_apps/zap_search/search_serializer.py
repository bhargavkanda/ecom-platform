from rest_framework import serializers

from zap_apps.zap_search.models import SearchString


class SearchStringSerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchString
        field = '__all__'