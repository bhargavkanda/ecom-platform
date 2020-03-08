from django.contrib import admin
from zap_apps.zap_analytics.models import *
# Register your models here.

class AnalyticsSessionsAdmin(admin.ModelAdmin):
	fields = ('unique_session', 'user', 'platform', 'start_timestamp', 'end_timestamp', 'start_page', 'end_page', 'device_id', 'source', 'campaign',)
	readonly_fields = ('start_timestamp',)

class AnalyticsEventsAdmin(admin.ModelAdmin):
	fields = ('name', 'session', 'timestamp', 'event_details',)
	readonly_fields = ('timestamp',)
  
admin.site.register(AnalyticsSessions, AnalyticsSessionsAdmin)
admin.site.register(AnalyticsEvents, AnalyticsEventsAdmin)
admin.site.register(ProductAnalytics)
admin.site.register(ImpressionAnalytics)
admin.site.register(ClevertapEvents)