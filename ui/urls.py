from django.conf.urls import patterns, url

from ui import views

urlpatterns = patterns('',
    # ex: /ui/
    url(r'^$', views.index, name='index'),
    # ex: /ui/index?host=5
    url(r'^index$', views.index, name='index'),
    # ex: /ui/5/
    url(r'^(?P<title_id>\d+)/$', views.webtitledetail, name='webtitledetail'),
    # ex: /ui/image/5
    url(r'^image/(?P<image_id>\d+)$', views.webimagedetail, name='webimagedetail')
)
