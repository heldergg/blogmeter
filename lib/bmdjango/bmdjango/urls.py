# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'meter.views.current_result', name='current_result'),

    # Blogmeter specific:
    (r'^mt/', include('meter.urls')),
)
