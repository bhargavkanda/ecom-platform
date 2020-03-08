from django.conf.urls import patterns, url
from zap_apps.order import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^myorders(/?)$', views.GetOrders.as_view()),
    url(r'^details/(?P<id>[0-9]*?)(/?)$', views.OrderDetails.as_view()),
    url(r'^transaction(/?)$', views.Transaction.as_view()),
    url(r'^pincode(/?)$', views.Pincode.as_view()),
    url(r'^rate_order(/?)$', views.RateOrder.as_view()),
    url(r'^order_tracker(/?)$', views.TrackOrder.as_view()),
    url(r'^(?P<order_id>[a-zA-Z]*[0-9]*)(/?)$', views.OrderSummary.as_view()),
    # url(r'^(?P<order_id>[0-9]*)(/?)$', views.OrderSummary.as_view()),
    # url(r'^juspay_order(/?)$', views.JuspayOrder.as_view()),
    url(r'^emi_option(/?)$', views.EMI_Payment.as_view()),
]
