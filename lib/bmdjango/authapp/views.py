# -*- coding: utf-8 -*-

"""Authentication forms"""

# Global imports
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
import datetime, time

# Local imports
from authapp.forms import AuthFormPersistent
from authapp.models import AccessAttempt

@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthFormPersistent):
    '''Displays the login form and handles the login action.'''

    # For each IP create a log line with login information
    remote_ip = request.META['REMOTE_ADDR']
    obj, created = AccessAttempt.objects.get_or_create(ip_address=remote_ip)

    show_captcha = ( obj.failures >= settings.FAILURE_LIMIT)

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST, show_captcha=show_captcha)

        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            from django.contrib.auth import login
            login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if form.cleaned_data['autologin']:
                request.session.set_expiry( settings.SESSION_COOKIE_AGE )
            else:
                request.session.set_expiry(0)

            # Resets the failed attempts
            obj.delete()

            return HttpResponseRedirect(redirect_to)
        else:
            obj.failures += 1
            if (obj.failures > settings.FAILURE_LIMIT) and not show_captcha:
                show_captcha = True
                form = authentication_form(data=request.POST, show_captcha=show_captcha)
            obj.save()
    else:
        form = authentication_form(request, show_captcha=show_captcha)

    request.session.set_test_cookie()

    if show_captcha:
        # Time penalty for multiple failed logins
        time.sleep(5)

    return render_to_response(template_name, {
        'form': form,
        'auth_error': '__all__' in form.errors,
        redirect_field_name: redirect_to,
        }, context_instance=RequestContext(request))

# TODO: when loging out on a restricted area we should be redirected to the
# index page instead of the "permission denied" page.

def logout(request, next_page=None,
    template_name='logout.html',
    redirect_field_name=REDIRECT_FIELD_NAME):
    '''Logs out the user and displays 'You are logged out' message.i'''

    from django.contrib.auth import logout
    logout(request)
    if next_page is None:
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        if redirect_to:
            return HttpResponseRedirect(redirect_to)
        else:
            return render_to_response(template_name, {
                'title': 'Logged out'
            }, context_instance=RequestContext(request))
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect( next_page or request.path)
