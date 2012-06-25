# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('meter.views',
    # Archive access
    url(r'^(?P<dt>\d{4}-\d{2}-\d{2})/$', 'result_archive', name='result_archive' ),
    )

