from django.contrib import admin
from zap_apps.blog.models import *


class BlogCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

    class Meta:
        model = BlogCategory


class BlogTagAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

    class Meta:
        model = BlogTag


class BlogCommentAdmin(admin.ModelAdmin):
    readonly_fields = ['comment_time']
    list_display = ['blog_post', 'commented_by', 'comment', 'comment_time']

    class Meta:
        model = BlogComment


class BlogProductAdmin(admin.ModelAdmin):
    search_fields = ['id', 'blog', 'item']
    list_display = ['id', 'item', 'blog']


class BlogProductInline(admin.TabularInline):
    model = BlogProduct


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'status', 'author', 'published_time', 'approved']
    list_editable = ['approved']
    list_filter = ['category', 'status', 'approved']
    search_fields = ['id', 'title', 'author__id', 'author__name']
    readonly_fields = ['status']
    inlines = [BlogProductInline, ]

    class Meta:
        model = BlogPost


class BlogLoveAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'user', 'device', 'time']
    readonly_fields = ['time']
    search_fields = ['blog_post__id']

    class Meta:
        model = BlogLove


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']
    search_fields = ['email']

    class Meta:
        model = Subscriber

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', '__unicode__', 'description']

admin.site.register(BloggersMeetUpRegistration)
admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogProduct, BlogProductAdmin)
admin.site.register(BlogTag, BlogTagAdmin)
admin.site.register(BlogLove, BlogLoveAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Subscriber, SubscriberAdmin)