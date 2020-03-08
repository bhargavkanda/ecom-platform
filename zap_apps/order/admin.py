from django.contrib import admin
from django import forms
from zap_apps.order.models import Transaction, Order, Return, OrderedProduct, OrderTracker
admin.site.register([Return, OrderedProduct])


class OrdersInline(admin.TabularInline):
    model = Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction', 'order_number', 'placed_at', 'product', 'final_price', 'order_status', 'delivery_date']
    list_filter = ['order_status', 'offer']
    list_editable = ['order_status', 'delivery_date']
    search_fields = ['id', 'order_number']

    class Meta:
        model = Order


class MyAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'payment_mode', 'time', 'transaction_ref', 'status', 'final_price', 'platform', 'offer']
    list_filter = ['payment_mode', 'status', 'platform', 'offer']
    search_fields = ['id', 'buyer__id', 'transaction_ref']
    inlines = [OrdersInline,]
    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        return qs
        

class OrderTrackerAdmin(admin.ModelAdmin):
    search_fields = ['orders__id', 'returns__id']


admin.site.register(Transaction, MyAdmin)
admin.site.register(OrderTracker, OrderTrackerAdmin)
admin.site.register(Order, OrderAdmin)
# Register your models here.
