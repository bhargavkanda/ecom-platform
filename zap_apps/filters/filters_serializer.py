from zap_apps.zap_catalogue.models import (Category, SubCategory,
                                           Brand, Style, Color, Occasion, AGE, CONDITIONS)
from rest_framework import serializers

class FilterCategorySeriaizer(serializers.ModelSerializer):
    sub_cats = serializers.SerializerMethodField('get_sub_categories')
    value = serializers.SerializerMethodField()
    # sub_cats = sort_subcat(sub_cats)

    def sort_subcat(sub_cats):
        sub_cats.sort(sub_cats, key=lambda y: y['disabled'])
    def get_value(self, obj):
        if not self.context['srlzr_change_cond']:
            return []
        selected_cat = self.context['selected_cat']
        filtered_sub_list = self.context['filtered_subcategory_list']
        all_sub_cat_dict = self.context['all_sub_category_dict']
        all_sub = all_sub_cat_dict.get(obj.id)
        # print all_sub

        return sorted(FilterSubCategorySerializer(all_sub, many=True, 
            context={'selected_cat': selected_cat,
            'filtered_subcategory_list': filtered_sub_list}).data, key=lambda y: y['disabled'])

    def get_sub_categories(self, obj):
        # sub_cat_dict = self.context['sub_category_dict']
        if self.context['srlzr_change_cond']:
            return []
        selected_cat = self.context['selected_cat']
        filtered_sub_list = self.context['filtered_subcategory_list']
        all_sub_cat_dict = self.context['all_sub_category_dict']
        all_sub = all_sub_cat_dict.get(obj.id)
        # print all_sub

        return sorted(FilterSubCategorySerializer(all_sub, many=True, 
            context={'selected_cat': selected_cat,
            'filtered_subcategory_list': filtered_sub_list}).data, key=lambda y: y['disabled'])

    class Meta:

        model = Category
        fields = ('id', 'name', 'category_type', 'sub_cats', 'value')


class FilterSubCategorySerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()

    def get_selected(self, foo):
        selected_cat = self.context['selected_cat']
        return foo.id in selected_cat

    def get_disabled(self, foo):
        filtered_sub_list = self.context['filtered_subcategory_list']
        return not foo.id in filtered_sub_list

    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'selected', 'disabled')


class FilterBrandSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    # brand = serializers.SerializerMethodField()

    def get_selected(self, foo):
        selected_brand = self.context['selected_brand']
        return foo.id in selected_brand

    def get_disabled(self, foo):
        filtered_brand_list = self.context['filtered_brand_list']
        return not foo.id in filtered_brand_list
    def get_name(self, foo):
        return foo.brand

    class Meta:
        model = Brand
        fields = ('id', 'name', 'selected', 'disabled')


class FilterStyleSerializer(serializers.ModelSerializer):

    selected = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_selected(self, foo):
        selected_style = self.context['selected_style']
        return foo.id in selected_style

    def get_disabled(self, foo):
        filtered_style_list = self.context['filtered_style_list']
        return not foo.id in filtered_style_list
    def get_name(self, foo):
        return foo.style_type

    class Meta:
        model = Style
        fields = ('id', 'name', 'selected', 'disabled')


class FilterColorSerializer(serializers.ModelSerializer):

    selected = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()

    def get_selected(self, foo):
        selected_color = self.context['selected_color']
        return foo.id in selected_color

    def get_disabled(self, foo):
        filtered_color_list = self.context['filtered_color_list']
        return not foo.id in filtered_color_list

    class Meta:
        model = Color
        fields = ('id', 'name', 'code', 'selected', 'disabled')


class FilterOccasionSerializer(serializers.ModelSerializer):

    selected = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()

    def get_selected(self, foo):
        selected_occasion = self.context['selected_occasion']
        return foo.id in selected_occasion

    def get_disabled(self, foo):
        filtered_occasion_list = self.context['filtered_occasion_list']
        return not foo.id in filtered_occasion_list

    class Meta:
        model = Occasion
        fields = ('id', 'name', 'selected', 'disabled')
