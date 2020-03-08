from django.conf.urls import patterns, url
from zap_apps.cart import views

urlpatterns = [

    url(r'^$', views.ZapCart.as_view()),
    url(r'^checkout/$', views.Checkout.as_view()),
    url(r'^quantity_availablity/$', views.ProductAvailability.as_view()),
]
