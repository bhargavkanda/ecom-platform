from django.contrib import admin
from .models import *


class NumberOfProductsAdmin(admin.ModelAdmin):
    search_fields = ['product__title', 'disapproved_product__title', 'product__id']


class NumberOfProductsInline(admin.TabularInline):
    model = NumberOfProducts


class ApprovedProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'user__zap_username', 'id']
    inlines = [NumberOfProductsInline,]
    list_display = ('title', 'pk', 'brand', 'status', 'condition', )

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        return qs
admin.site.register(NumberOfProducts, NumberOfProductsAdmin)
admin.site.register(ApprovedProduct, ApprovedProductAdmin)

admin.site.register(Category)


class SubCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)

admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Color)


class BrandAdmin(admin.ModelAdmin):
    search_fields = ['brand', 'id']
    readonly_fields = ('slug',)


class CommentsAdmin(admin.ModelAdmin):
    list_display = ['commented_by', 'comment', 'comment_time', 'product']
    search_fields = ['product__id', 'commented_by__id']


admin.site.register(Brand, BrandAdmin)
admin.site.register(Occasion)
admin.site.register(Style)
admin.site.register(Size)
admin.site.register(ProductImage)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Loves)
admin.site.register(Conversations)
