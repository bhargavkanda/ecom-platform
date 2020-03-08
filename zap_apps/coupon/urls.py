from django.conf.urls import patterns, url
from zap_apps.coupon import views

urlpatterns = [
    url(r'^apply(/?)$', views.Coupons.as_view()),
    url(r'^promo(/?)$', views.Promo.as_view()),
]
