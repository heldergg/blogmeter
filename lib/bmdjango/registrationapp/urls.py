'''Registration urls'''

from django.conf import settings
from django.conf.urls import patterns, url

urlpatterns = patterns('registrationapp.views',

    url(r'^$', 'registration', name='registration'),

    )
