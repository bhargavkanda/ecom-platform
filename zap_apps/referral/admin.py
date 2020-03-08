from django.contrib import admin
from zap_apps.referral.models import RefCode
# Register your models here.
from djcelery.models import TaskMeta
class TaskMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('result',)    
admin.site.register(TaskMeta, TaskMetaAdmin)

class RefCodeMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('result',)    
admin.site.register(RefCode)