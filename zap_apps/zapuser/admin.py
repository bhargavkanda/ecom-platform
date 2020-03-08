from django.contrib import admin
from .models import *
# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User


def user_unicode(self):
    return  '{}, {}'.format(self.email or "", (self.zapuser.zap_username, self.zapuser.id) if hasattr(self, 'zapuser') else "")

User.__unicode__ = user_unicode


class ZapUserAdmin(admin.ModelAdmin):
    search_fields = ['zap_username', 'email', 'phone_number']
    list_display = ['id', 'zap_username', 'email', 'phone_number', 'user_type']
    list_editable = ['user_type']

class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'phone_number']

admin.site.register(ZapUser, ZapUserAdmin)
admin.site.unregister(User)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserData)
admin.site.register(UserPreference)
admin.site.register(BrandTag)
admin.site.register(LoggedDevice)
admin.site.register(WebsiteLead)
admin.site.register(DesignerProfile)
admin.site.register(Subscriber, SubscriberAdmin)


class BranchTestAdmin(admin.ModelAdmin):
    list_display = ('content', 'source',)

class ZapExclusiveUserDataAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'account_holder',)

admin.site.register(ZapExclusiveUserData, ZapExclusiveUserDataAdmin)
admin.site.register(BranchTest, BranchTestAdmin)
admin.site.register([BuildNumber, ZAPGCMDevice, ZapRole, AppViralityKey, NewAppFeature, UserGroup])
