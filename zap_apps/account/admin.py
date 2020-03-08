from django.contrib import admin

from zap_apps.account.models import AppLinkSms, CallRequest, Testimonial
admin.site.login_template = 'admin/login.html'
admin.autodiscover()
admin.site.site_header = 'Zapyle administration login'

admin.site.register([AppLinkSms,CallRequest, Testimonial])

