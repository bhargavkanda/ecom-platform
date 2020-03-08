from zap_apps.marketing.models import *
from rest_framework_mongoengine import serializers
from rest_framework import serializers as srl


class ActionSerializer(serializers.DocumentSerializer):

 
    class Meta:
        model = Action
        fields = ('action_type', 'data')

class ConditionSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Condition
        fields = ('condition_type','value')

class NotifsSerializer(serializers.DocumentSerializer):
    # sub_cats = serializers.SerializerMethodField('get_sub_categories')

    # def get_sub_categories(self, obj):
    #     sub_cat_dict = self.context['sub_category_dict']
    #     count_dict = self.context['count_dict']
    #     filtered_sub = sub_cat_dict.get(obj.id)
        

    #     return FilterSubCategorySerializer(filtered_sub, many=True, context={'count_dict':count_dict}).data
    action = ActionSerializer(many=False)
    condition = ConditionSerializer(many=True, required=False)


    class Meta:
        model = Notifs
        fields = ('id','text', 'tag', 'scheduled_time', 'action', 'condition')
        depth = 2


class OverlaySerializer(srl.ModelSerializer):
    action = srl.SerializerMethodField()
    image_resolution = srl.SerializerMethodField()
    image = srl.SerializerMethodField()

    def get_action(self,obj):
        return {
            'action_type':obj.action.action_type or '', 
            'ios_target':obj.action.ios_target,
            'target':obj.action.ios_target
        }

    def get_image_resolution(self, foo):
        return {'width': foo.image_width, 'height': foo.image_height}

    def get_image(self, obj):
        return obj.image.url

    class Meta:
        model = Overlay
        field = ('image', 'image_resolution', 'title', 'description', 'cta_text', 
            'start_date', 'end_date', 'active', 'platform', 'can_close', 'delay', 'page', 
            'campaign', 'full_screen', 'uri_target', 'activity_name', 'action', 'android_activity')

class CampaignSerializer(srl.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ('following_users')
        