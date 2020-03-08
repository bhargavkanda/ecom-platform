from django.conf.urls import patterns, url
from zap_apps.account import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    url(r'^login/$', views.ZapLogin.as_view()),
    url(r'^signup/?$', views.ZapSignup.as_view()),
    url(r'^reducedsignup/?$', views.ZapReducedSignup.as_view()),
    url(r'^logout/?$', views.ZapLogout.as_view()),
    url(r'^password/reset/?$', views.ZapResetPassword.as_view()),
    url(r"^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$",
        views.ZapPasswordResetTokenView.as_view(), name="account_password_reset_token"),

    url(r'^instagram/?$', views.InstagramRedirectView.as_view()),
    url(r'^instagram/login/?$', views.InstagramLogin.as_view()),
    url(r'^instagram/checkoutlogin/?$', views.InstagramCheckoutLogin.as_view()),
    # url(r'^forgetpassword(/?)$', views.ForgetPassword.as_view()),
    url(r'^zapotp/get/(?P<mobno>\+*\d+)(/?)$', views.ZapGetOtp.as_view()),

    # url(r'^zapotp(/?)$', views.ZapOtp.as_view()),
    url(r'^test(/?)$', views.Test.as_view()),
    url(r'^call(/?)$', views.Call.as_view()),
    # url(r'^testimonial(/?)$', views.TestimonialView.as_view()),
]
