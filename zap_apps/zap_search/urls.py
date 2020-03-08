from django.conf.urls import patterns, url
from zap_apps.zap_search import views

urlpatterns = [
    url(r'^(?P<result_type>product|closet|blog)(/?)((?P<product_type>zap_market|zap_curated)?)(/?)$', views.Search.as_view()),
    url(r'^(?i)suggestions/(?P<suggestion_tab>product|closet|blog)(/?)$', views.Suggestions.as_view()),
    url(r'^history/(/?)$', views.SearchHistory.as_view()),
]
