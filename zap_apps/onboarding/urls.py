from django.conf.urls import patterns, url
from zap_apps.onboarding import views

urlpatterns = [

    url(r'^(?P<step>[1,2,3,4])(/?)$', views.OnboardingView.as_view()),
    # url(r'^$', views.Onboardings.as_view()),
    url(r'^getbrandtags(/?)$', views.GetBrandTags.as_view()),
    url(r'^getbrands(/?)$', views.GetAllBrand.as_view()),
    url(r'^getcolors(/?)$', views.GetAllColors.as_view()),
    url(r'^getstyles(/?)$', views.GetAllStyles.as_view()),
    url(r'^getoccasions(/?)$', views.GetAllOccasions.as_view()),
    url(r'^getoccasions(/?)$', views.GetAllOccasions.as_view()),
    url(r'^getcategories(/?)$', views.GetAllCategories.as_view()),
]
