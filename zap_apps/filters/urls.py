from django.conf.urls import patterns, url
from zap_apps.filters import views

urlpatterns = [

    url(r'^getFilters/(?P<filter_type>[a-z_]+)/((?P<page_type>category|brand)?)(/?)$', views.Filters.as_view()),
    url(r'^getEFilters/(?P<filter_type>[a-z_]+)/((?P<page_type>category|brand)?)(/?)$', views.ElasticFilters.as_view()),
    url(r'^getInitialFilters/', views.InitialFilters.as_view()),
    url(r'^getProducts/(?P<page>[0-9]*)(/?)an/((?P<page_type>category|brand|sub-category)?)(/?)$', views.AnProducts.as_view()),
    url(r'^getProducts/(?P<page>[0-9]*)/((?P<page_type>category|brand|sub-category)?)(/?)$', views.Products.as_view()),
    url(r'^getEProducts/(?P<page>[0-9]*)/((?P<page_type>category|brand|sub-category)?)(/?)$', views.ElasticProducts.as_view()),
    url(r'^getProducts/(?P<page>[0-9]*)/an(/?)((?P<page_type>zap_market|zap_curated|designer)?)(/?)$', views.AnProducts.as_view()),
    url(r'^f_o/$', views.webFilterItems.as_view()),
    url(r'^webFilterItems/$', views.webFilterItems1.as_view()),
    url(r'^get_love_and_offer/$',views.GetLoveAndOffer.as_view())
]