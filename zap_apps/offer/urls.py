from django.conf.urls import patterns, url
from zap_apps.offer import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^apply/(?P<offer_id>.+)(/?)$', views.ApplyOffer.as_view()),
]