# -*- coding: utf-8 -*-

'''Registration views'''

# Global imports
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.forms.util import ErrorList

# Local imports
from registrationapp.forms import RegistrationForm

@csrf_protect
@never_cache
def registration(request):
    '''User registration.'''
    context= {}

    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    context['next'] = redirect_to

    # User Info
    remote_ip = request.META['REMOTE_ADDR']

    if request.method == 'POST':
        new_data = request.POST.copy()
        form = RegistrationForm(remote_ip, new_data)
        if form.is_valid():
            data = form.cleaned_data

            # Check if user exists and creates if not
            user = User.objects.filter(username=data['username'])
            if user:
                form._errors['username'] = ErrorList([u'Um utilizador com o nome %s já existe'%data['username']])
                context['form']=form
                return render_to_response('registration.html',
                    context, context_instance=RequestContext(request))

            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            new_user = User.objects.create_user(data['username'], data['email'], data['password_1'])

            # Login user and send to origin page
            new_user_auth = authenticate(username=data['username'], password=data['password_1'])
            login(request, new_user_auth)
            return HttpResponseRedirect(redirect_to)
        else:
            context['form']=form
    else:
        form = RegistrationForm(remote_ip)
        context['form']=form

    return render_to_response('registration.html',
        context, context_instance=RequestContext(request))
