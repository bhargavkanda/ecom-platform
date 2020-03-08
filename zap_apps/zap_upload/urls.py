from django.conf.urls import patterns, url
from zap_apps.zap_upload import views

urlpatterns = [
    url(r'^album/(?P<product_id>[0-9]*?)(/?)$', views.AlbumCRUD.as_view()),
    url(r'^pro_pic(/?)$', views.ProPic.as_view()),
    url(r'^album/(?P<product_id>[0-9]*?)(/?)(?P<step>[0-9]*?)(/?)$',
        views.EditAlbum.as_view()),
    url(r'^album/image/(?P<product_id>[0-9]*?)(/?)$', views.ImageUpload.as_view()),

]
