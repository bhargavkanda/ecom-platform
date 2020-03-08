from django.conf.urls import patterns, url
from zap_apps.payment import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^confirmorder(/?)(?P<t_ref>[0-9]*?)(/?)$',
        views.BillGenerator.as_view()),
    url(r'^confirmorder/website(/?)$', views.WebsiteBillGenerator.as_view()),
    url(r'^zappaymentreturn(/?)$', csrf_exempt(views.ReturnUrl.as_view())),
    url(r'^zappaymentreturn/website(/?)$',
        csrf_exempt(views.WebsiteReturnUrl.as_view())),
    url(r'^zappaymentreturn/juspay/website(/?)$',
        csrf_exempt(views.JuspayWebsiteReturnUrl.as_view())),
    url(r'summary(/?)$', views.PaymentSummary.as_view()),
    url(r'get_accesskey_vanity(/?)$', views.AccessKeyVanity.as_view()),
    url(r'^confirmorder/website/retry/(?P<tx_id>[0-9]*?)(/?)$', views.RetryPayment.as_view()),
    url(r'^cod(/?)$',
        views.CodGenerator.as_view()),
    url(r'^refund/$', csrf_exempt(views.Refund.as_view())),
    url(r'^notify/website(/?)$',
        csrf_exempt(views.WebsiteNotifyUrl.as_view())),
    
]
