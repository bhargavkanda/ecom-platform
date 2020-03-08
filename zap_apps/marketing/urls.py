from django.conf.urls import patterns, url
from zap_apps.marketing import views

urlpatterns = [

    # url(r'^(?P<step>[1,2,3,4])(/?)$', views.OnboardingView.as_view()),
    # # url(r'^$', views.Onboardings.as_view()),
    # url(r'^getbrandtags(/?)$', views.GetBrandTags.as_view()),
    url(r'^track(/?)$', views.SaveNotifTrack.as_view()),
    url(r'^overlay/?(?P<page>\w+)/?$', views.OverlayView.as_view()),
    url(r'^campaign/?(?P<campaign_id>\w+)/?$', views.FollowCampaign.as_view()),
    url(r'^follow_campaign(/?)$', views.FollowCampaignAllUsers.as_view()),
    url(r'^verify_lead', views.verify_lead, name='verify_lead'),
]