from django.conf.urls import patterns, url

from zap_apps.zap_analytics import views

urlpatterns = [
    url(r'^(?P<track_item>product | user)(/?)$', views.Analytics.as_view()),
    url(r'^recently_viewed_products/$', views.RecentProductViewed.as_view()),
    url(r'^initiate_analytics_session/$', views.InitiateAnalyticsSession.as_view()),
    url(r'^end_analytics_session/$', views.EndAnalyticsSession.as_view()),
    url(r'^track_analytics_events/$', views.TrackAnalyticsEvents.as_view()),
    url(r'^seller_analytics/$', views.SellerAnalytics.as_view()),
    url(r'^download_seller_analytics/$', views.DownloadSellerAnalytics.as_view()),
]