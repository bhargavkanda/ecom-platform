from rest_framework import serializers
from zap_apps.blog.models import *
import re
from zap_apps.zap_commons.common_serializers import ZapErrorModelSrlzr
from zap_apps.zapuser.zapuser_serializer import UserSerializer
from zap_apps.zapuser.models import ZapUser
from datetime import datetime, timedelta


class BlogTagSrlzr(serializers.ModelSerializer):

    class Meta:
        model = BlogTag
        fields = ('name',)
        read_only_fields = ('id',)


class SingleBlogPostSrlzr(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    loved_by_user = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    love_count = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    def get_products(self, obj):
        from zap_apps.zap_catalogue.models import ApprovedProduct
        from zap_apps.zap_catalogue.product_serializer import LookProductSerializer
        product_ids = obj.blog_products.all().values_list('item', flat=True)
        products = ApprovedProduct.ap_objects.filter(id__in=product_ids)
        if 'user' in self.context:
            serializer = LookProductSerializer(products, many=True, context={'user': self.context['user']})
        else:
            serializer = LookProductSerializer(products, many=True, context={})
        return serializer.data

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name, 'slug': obj.category.slug} if obj.category else None

    def get_time(self, obj):
        return obj.time

    def get_loved_by_user(self, obj):
        if 'user' in self.context:
            user = self.context['user']
            try:
                obj.loves.get(user=user)
                return True
            except Exception:
                return False
        return False

    def get_author_name(self, obj):
        return obj.author.name if obj.author else None

    def get_love_count(self, obj):
        return obj.loves.all().count()

    def get_editable(self, obj):
        if 'user' in self.context:
            current_user = self.context['user']
            return ((current_user == obj.author.user if obj.author else False) or current_user.is_superuser)
        return False

    def get_slug(self, obj):
        return obj.title.lower().replace(' ', '-')

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'body', 'author', 'category', 'tags', 'cover_pic', 'status', 'published_time',
                  'created_time', 'updated_time', 'products', 'time', 'loved_by_user', 'author_name', 'love_count',
                  'editable', 'slug']


class BlogListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    loved_by_user = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    cover_pic = serializers.SerializerMethodField()

    def get_category(self, obj):
        return {'slug': obj.category.slug, 'name': obj.category.name} if obj.category else None

    def get_loved_by_user(self, obj):
        if 'user' in self.context:
            user = self.context['user']
            try:
                obj.loves.get(user=user)
                return True
            except Exception:
                return False
        return False

    def get_time(self, obj):
        return obj.time

    def get_slug(self, obj):
        return obj.slug

    def get_editable(self, obj):
        if 'user' in self.context:
            current_user = self.context['user']
            return ((current_user == obj.author.user if obj.author else False) or current_user.is_superuser)
        return False

    def get_author(self, obj):
        return {'id': obj.author.id, 'name': obj.author.name} if obj.author else None

    def get_cover_pic(self, obj):
        return obj.cover_pic_small

    class Meta:
        model = BlogPost
        fields = ['id', 'slug', 'title', 'cover_pic', 'category', 'loved_by_user', 'time', 'editable', 'approved', 'author']


class BlogPostSrlzr(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    def get_products(self, obj):
        from zap_apps.zap_catalogue.models import ApprovedProduct
        from zap_apps.zap_catalogue.product_serializer import LookProductSerializer
        product_ids = obj.blog_products.all().values_list('item', flat=True)
        products = ApprovedProduct.ap_objects.filter(id__in=product_ids)
        serializer = LookProductSerializer(products, many=True)
        return serializer.data

    def validate(self, data):
        from django.forms.models import model_to_dict
        if self.instance is not None:
            instance = self.instance
        else:
            instance = BlogPost()
        post_data = model_to_dict(instance)
        post_data.update({'products': instance.blog_products.all().values_list('item', flat=True)})
        for key in data.keys():
            post_data[key] = data[key]
        if post_data['status'] == 'PB':
            if post_data['body'] == '' or not post_data['body']:
                raise serializers.ValidationError({'error': 'Body cannot be empty when you publish.'})
            if post_data['category'] == '' or not post_data['category']:
                raise serializers.ValidationError({'error': 'Category cannot be empty when you publish.'})
            if post_data['cover_pic'] == '' or not post_data['cover_pic']:
                raise serializers.ValidationError({'error': 'Cover pic cannot be empty when you publish.'})
            if post_data['author'] == '' or not post_data['author']:
                raise serializers.ValidationError({'error': 'Author cannot be empty when you publish.'})
            if instance.category.slug == 'look-book' and len(post_data['products']) == 0:
                raise serializers.ValidationError({'error': 'Products cannot be empty when you publish a look.'})
        return data

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'body', 'author', 'category', 'tags', 'cover_pic', 'status', 'published_time',
                  'created_time', 'updated_time', 'products', 'approved']


class BlogPostMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogPost
        fields = ['author', 'category', 'tags', 'cover_pic']


class BlogCategorySrlzr(serializers.ModelSerializer):

    class Meta:
        model = BlogCategory
        fields = '__all__'


class AuthorSrlzr(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.name

    class Meta:
        model = Author
        fields = ['id', 'name', 'description', 'profile_pic', 'user']