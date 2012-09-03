# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('meter.views',
    # Archive access
    url(r'^(?P<dt>\d{4}-\d{2}-\d{2})/$', 'result_archive', name='result_archive' ),
    # Blog Highlight
    url(r'^highlight/(?P<dt>\d{4}-\d{2}-\d{2})/(?P<blog_id>\d+)/$', 'blog_highlight', name='blog_highlight' ),
    url(r'^highlight/(?P<blog_id>\d+)/$', 'highlight_today', name='highlight_today' ),
    # Blog search
    url(r'^procurar/$', 'blog_search', name='blog_search' ),
    # Blog info
    url(r'^info/(?P<blog_id>\d+)/$', 'blog_info', name='blog_info' ),
    )

