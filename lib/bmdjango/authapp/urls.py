
from django.conf import settings
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('authapp.views',

    url(r'^login/$', 'login',
        {'template_name': 'login.html'}, name='login'),

    url(r'^logout/$', 'logout', name='logout'),
    )
