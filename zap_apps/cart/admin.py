from django.contrib import admin
from zap_apps.cart.models import Cart, Item

class CartItemAdmin(admin.ModelAdmin):
    search_fields = ['cart__user__zap_username', 'cart__user__email', 'product__title']
    list_display = ('cart', 'product', 'size', 'offer', 'added_at')

class CartItemInline(admin.TabularInline):
    model = Item

class CartAdmin(admin.ModelAdmin):
    search_fields = ['user__zap_username', 'user__email', 'product__title']
    list_display = ['id', 'user', 'offer']
    inlines = [CartItemInline, ]

# Register your models here.
admin.site.register(Item, CartItemAdmin)
admin.site.register(Cart, CartAdmin)
