from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from zap_apps.marketing.models import UserMarketing, Overlay, ClosetCleanup, ActionDefault, Campaign, CampaignProducts, OverlaySeen, Lead

# Register your models here.
admin.site.register([UserMarketing, Overlay, ClosetCleanup, ActionDefault, OverlaySeen])

class CampaignProductsAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'discount', 'products')

class CampaignProductsInline(admin.TabularInline):
    model = CampaignProducts

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'offer')
    inlines = [CampaignProductsInline,]

admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignProducts, CampaignProductsAdmin)

class LeadAdmin(admin.ModelAdmin):
    list_display = ('email', 'unique_code', 'referral_user', 'referral_lead', 'acquired_campaign', 'verified', 'source')
    readonly_fields = ('unique_code',)

admin.site.register(Lead, LeadAdmin)