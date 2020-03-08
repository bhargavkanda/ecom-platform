from django.conf.urls import patterns, url
from zap_apps.zap_notification.views import *
from zap_apps.zap_notification import views

urlpatterns = [
    url(r'^send_sms/?$', SendSMS),
    url(r'^send_email/?$', SendEMAIL),
    url(r'^send_push_data/?$', SendPushData),
    url(r'^getmynotifs/?$', views.GetMyNotifs.as_view()),
    url(r'^getmynotifs/(?P<page>[0-9]*)(/?)$', views.GetMyNotifs.as_view()),
    url(r'^readnotif(/?)$', views.ReadNotification.as_view()),
]