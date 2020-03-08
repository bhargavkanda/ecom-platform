from django.conf.urls import patterns, url
from zap_apps.discover import views

urlpatterns = [
    
    url(r'^(/?)$', views.Discover.as_view()),
    # url(r'^/website_home(/?)$', views.WebsiteHome.as_view()),
    ]