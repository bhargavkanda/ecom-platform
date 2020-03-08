from django.contrib import admin
from .models import *

# Register your models here.
class HomefeedAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'active', 'platform', 'importance', 'start_time', 'end_time',)
    list_filter = ['active', 'platform', 'show_in']
    list_editable = ['active', 'importance', 'start_time', 'end_time', 'platform']

admin.site.register(Homefeed, HomefeedAdmin)

admin.site.register([ZapAction, Banner, Message, ProductCollection,
                     UserCollection, Closet, CustomCollection, Generic, CTA, Screens])
