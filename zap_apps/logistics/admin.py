from django.contrib import admin
from zap_apps.logistics.models import Logistics, LogisticsLog, AramexStatus, DelhiveryPincode
admin.site.register([Logistics, LogisticsLog, AramexStatus, DelhiveryPincode])
# Register your models here.
