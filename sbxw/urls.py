from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sbxw.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^ui/', include('ui.urls', namespace="ui")),
    url(r'^admin/', include(admin.site.urls)),
)
