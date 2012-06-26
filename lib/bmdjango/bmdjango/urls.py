# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    # The index view
    url(r'^$', 'meter.views.current_result', name='current_result'),

    # Blogmeter specific:
    (r'^mt/', include('meter.urls')),

    # AboutView
    url(r'^about/', TemplateView.as_view(template_name="about.html"), name='about'),
)
