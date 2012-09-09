# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # The index view
    url(r'^$', 'meter.views.current_result', name='current_result'),

    # Blogmeter specific:
    (r'^mt/', include('meter.urls')),

    # Authenticated Interface
    (r'^auth/', include('authapp.urls')),

    # Registration Interface
    (r'^registar/', include('registrationapp.urls')),

    # AboutView
    url(r'^about/', TemplateView.as_view(template_name="about.html"), name='about'),

    # FAQ view
    url(r'^faq/', TemplateView.as_view(template_name="faq.html"), name='faq'),

    # Admin views
    url(r'^admin/', include(admin.site.urls)), 
)
