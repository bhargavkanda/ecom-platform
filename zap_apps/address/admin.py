from django.contrib import admin

# Register your models here.
from zap_apps.address.models import State, Address, CityPincode
admin.site.register(CityPincode)
class ZapWalletAddress(admin.ModelAdmin):
    search_fields = ['user__zap_username','user__email']
    # inlines = [NumberOfProductsInline,]
    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        return qs
admin.site.register(Address, ZapWalletAddress)