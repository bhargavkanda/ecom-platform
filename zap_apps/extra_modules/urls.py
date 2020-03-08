from django.conf.urls import patterns, url
from zap_apps.extra_modules import views 

urlpatterns = [
    url(r'^appvirality/conversion/$', views.AppViralityConversion.as_view()),
    url(r'^appvirality/frienreward/$', views.AppViralityFriendReward.as_view()),
    url(r'^appvirality/referrerreward/$', views.AppViralityReferrerReward.as_view()),
    url(r'^appvirality/campaign/?$', views.AppViralityCampaign.as_view()),
]