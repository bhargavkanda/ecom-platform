from django.contrib import admin
from zap_apps.payment.models import PaymentResponse, ZapWallet, Payout, RefundResponse
admin.site.register(PaymentResponse)
# admin.site.register(ZapWallet)
admin.site.register(Payout)
admin.site.register(RefundResponse)
class ZapWalletSearch(admin.ModelAdmin):
    search_fields = ['user__zap_username','user__email','promo__code']
    list_display = ['user', 'amount', 'credit', 'mode', 'promo', 'purpose']
    list_filter = ['user', 'credit', 'mode', 'promo']
    list_editable = ['mode']
    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        return qs
admin.site.register(ZapWallet, ZapWalletSearch)
