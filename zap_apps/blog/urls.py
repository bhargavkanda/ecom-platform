from django.conf.urls import patterns, url
from zap_apps.blog import views
from zap_apps.blog.views import home

urlpatterns = [
    url(r'^image(/?)$', views.Image.as_view()),
    url(r'^post/$', views.BlogCRUD.as_view()),
    url(r'^post/(?P<post_id>[0-9]+)/$', views.BlogCRUD.as_view()),
    url(r'^categories/$', views.BlogCategoryCRUD.as_view()),
    url(r'^tags/$', views.BlogTagCRUD.as_view()),
    url(r'^posts/$', views.BlogPosts.as_view()),
    # url(r'^post/(?P<blog_id>[0-9]+)/$', views.SingleBlog.as_view()),
    url(r'^meta_data(/?)(?P<blog_id>[0-9]*)(/?)$', views.PostData.as_view()),
    url(r'^next_blog(/?)(?P<blog_id>[0-9]*)(/?)$', views.NextBlog.as_view()),
    url(r'^love_blog(/?)(?P<blog_id>[0-9]*)(/?)$', views.BlogLove.as_view()),
    url(r'^related(/?)(?P<product_id>[0-9]*)(/?)$', views.RelatedBlogs.as_view()),
]