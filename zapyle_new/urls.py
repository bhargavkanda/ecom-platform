"""zapyle_new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from zap_apps.zap_catalogue.views import *
from zap_apps.discover.views import *
from zap_apps.zap_search.views import *
from zap_apps.zap_catalogue.views import *
from zap_apps.extra_modules.views import *
from zap_apps.zap_upload.views import *
from zap_apps.blog.views import *
from zap_apps.zapimport.views import *
from zap_apps.marketing.views import *
from zap_apps.coupon.views import *
from zap_apps.referral.views import *
from zap_apps.account.views import *
from zap_apps.zap_admin.views import *
from zap_apps.zap_analytics import views
from zap_apps.zap_catalogue import views

urlpatterns = [
	url(r'^(?P<page>(events)*)(/?)$', 'zap_apps.account.views.home', name='home'),
    url(r'^sell', sell),
    url(r'^(?P<list>shop|brand|category)(/)$', 'zap_apps.zap_catalogue.views.lists'),
    url(r'^(?P<filter>shop|brand|category|sub-category)/(?P<value>.+)/(?P<list>shop|brand|category)(/)$', 'zap_apps.zap_catalogue.views.lists'),
    
    ############# URLs for ELASTICSEARCH Filter ###############
    url(r'^buy(/?)$', elastic_shops),
    url(r'^(?P<filter>shop|brand|category|collection|sub-category)/(?P<value>.+)(/)(?P<filter2>brand|category|collection|sub-category)(/)(?P<value2>.+)(/)$', 'zap_apps.zap_catalogue.views.elastic_shops'),
    url(r'^(?P<filter>shop|brand|category|collection|sub-category)/(?P<value>.+)(/)$', 'zap_apps.zap_catalogue.views.elastic_shops'),

    ############# URLs for Normal Filter ######################
    # url(r'^buy(/?)$', shops),
    # url(r'^(?P<filter>shop|brand|category|collection|sub-category)/(?P<value>.+)(/)(?P<filter2>brand|category|collection|sub-category)(/)(?P<value2>.+)(/)$', 'zap_apps.zap_catalogue.views.shops'),
    # url(r'^(?P<filter>shop|brand|category|collection|sub-category)/(?P<value>.+)(/)$', 'zap_apps.zap_catalogue.views.shops'),
    ############## end filter URLs ############################

    url(r'^product/(?P<id>[0-9]*)/(?P<title>.*)(/?)$', 'zap_apps.zap_catalogue.views.WebsiteProductView'),
    url(r'^profile/(?P<id>[0-9]*)/(?P<username>.*)(/?)$', 'zap_apps.zap_catalogue.views.WebsiteProfileView'),
    url(r'^my_loves', 'zap_apps.zap_catalogue.views.WebsiteLoveView'),
    url(r'^about-us', 'zap_apps.zap_catalogue.views.AboutUs'),
    url(r'^world-tour', 'zap_apps.zap_catalogue.views.WorldTour'),
    url(r'^subscribe', 'zap_apps.zap_catalogue.views.Subscribe'),
    url(r'^authenticity', 'zap_apps.zap_catalogue.views.Authenticity'),
    #blog Pages
    url(r'^(?P<type>blog|look)/post/(?P<blog_id>[0-9]+)/edit', 'zap_apps.blog.views.editor'),
    url(r'^blog/post/(?P<blog_id>[0-9]+)/(?P<blog_slug>.*)(/?)', 'zap_apps.blog.views.post'),
    url(r'^(?P<type>blog|look)/create(/?)', 'zap_apps.blog.views.editor'),
    url(r'^blog', 'zap_apps.blog.views.home'),
    #static pages
    url(r'^contact-us', views.ContactUs.as_view()),
    url(r'^terms-conditions', 'zap_apps.zap_catalogue.views.Terms'),
    #Redirect to App Urls
    url(r'^zapblog/', include('zap_apps.blog.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('zap_apps.account.urls')),
    url(r'^analytics(/?)', include('zap_apps.zap_analytics.urls')),
    url(r'^user/', include('zap_apps.zapuser.urls')),
    url(r'^address/', include('zap_apps.address.urls')),
    url(r'^catalogue/', include('zap_apps.zap_catalogue.urls')),
    url(r'^offer/', include('zap_apps.offer.urls')),
    url(r'^onboarding/', include('zap_apps.onboarding.urls')),
    url(r'^payment/', include('zap_apps.payment.urls')),
    url(r'^zapcart/', include('zap_apps.cart.urls')),
    url(r'^order/', include('zap_apps.order.urls')),
    url(r'^filters/', include('zap_apps.filters.urls')),
    url(r'^coupon/', include('zap_apps.coupon.urls')),
    url(r'^notif/', include('zap_apps.marketing.urls')),
    url(r'^marketing/', include('zap_apps.marketing.urls')),
    url(r'^notification/', include('zap_apps.zap_notification.urls')),
    url(r'^upload/', include('zap_apps.zap_upload.urls')),
    url(r'^zapimport/', include('zap_apps.zapimport.urls')),
    url(r'^download/', download, name='download'),
    url(r'^zapadmin/', include('zap_apps.zap_admin.urls')),
    url(r'^isreferral/$', referral, name='referral'),
    url(r'^bloggersmeetup/?$', BloggersMeetUp),
    url(r'^dashboard/?', Dashboard),
    url(r'^extra/', include('zap_apps.extra_modules.urls')),
    url(r'^search/', include('zap_apps.zap_search.urls')),
    url(r'^discover',include('zap_apps.discover.urls')),
    # url(r'^events',include('zap_apps.discover.urls')),
    url(r'^closet-cleanup-a/$', closet_cleanup),
    url(r'^closet-cleanup-b/$', closet_cleanup2),
    url(r'^get-free-tory-burch/$', get_free_tory_burch),
    url(r'^sitemap.xml$', sitemap_xml),
    url(r'^sp-push-manifest.json$', send_plus_manifest),
    url(r'^sp-push-worker.js$', send_plus_worker),
    url(r'^robots.txt$', robots_txt),
    url(r'^campaign/(?P<campaign_id>.*)/(?P<thanks_page>[a-z_]*?)$', international_treat),
    url(r'^home', home_jinja2),

]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = handler404
handler500 = handler500
handler403 = handler403
handler400 = handler500