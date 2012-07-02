# -*- coding: utf-8 -*-

"""Authentication forms"""


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from utils.recaptcha_newforms import RecaptchaFieldPlaceholder, RecaptchaField
from utils.middleware import threadlocals

class AuthFormPersistent(AuthenticationForm):
    def __init__(self, *args, **kargs):
        show_captcha = False
        if kargs.has_key('show_captcha'):
            show_captcha = kargs['show_captcha']
            del kargs['show_captcha']

        if show_captcha:
            self.base_fields['captcha'] = RecaptchaFieldPlaceholder(label='Humano?')
            remote_ip = threadlocals.get_remote_ip()
            self.base_fields['captcha'] = RecaptchaField(remote_ip,
                        *self.base_fields['captcha'].args,
                        **self.base_fields['captcha'].kwargs)
        else:
            if 'captcha' in self.base_fields:
                del self.base_fields['captcha']

        super(AuthFormPersistent, self).__init__(*args, **kargs)


    autologin = forms.BooleanField(
        label = 'Login automatico?',
        required=False )
