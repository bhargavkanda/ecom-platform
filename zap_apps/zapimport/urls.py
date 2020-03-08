from django.conf.urls import patterns, url
from zap_apps.zapimport import views

urlpatterns = [
    url(r'^$', views.ZapImportHandler.as_view()),
]
