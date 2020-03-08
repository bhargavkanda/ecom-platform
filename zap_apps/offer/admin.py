from django.contrib import admin
from zap_apps.offer.models import ZapOffer,OfferBenefit, OfferCondition, ZapCredit
# Register your models here.
admin.site.register([OfferBenefit, OfferCondition, ZapCredit])

class ZapOfferAdmin(admin.ModelAdmin):
    list_display = ['code', 'offer_type', 'status', 'usage_per_user', 'offer_benefit', 'offer_condition']
    list_editable = ['status']
    list_filter = ['offer_type', 'status', 'offer_when']
    search_fields = ['code']

admin.site.register(ZapOffer, ZapOfferAdmin)