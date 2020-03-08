from django.conf.urls import patterns, url
from zap_apps.address import views

urlpatterns = [
    url(r'^crud(/?)$', views.AddressCRUD.as_view()),
    url(r'^get_states(/?)$', views.GetStates.as_view()),
    url(r'^check_pincode/(?P<pin>[0-9]*?)(/?)$', views.Pincode.as_view()),
    url(r'^pincode/$', views.GetCity.as_view()),
]
