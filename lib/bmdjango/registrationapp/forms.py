# -*- coding: utf-8 -*-

'''Registration forms'''

# Global
from django.conf import settings
from django import forms
from django.forms.util import ErrorList

# Local
from utils.recaptcha_newforms import RecaptchaForm

ALLOWEDCHARS = '!"#$%&/()=@{[]}\'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789'

class RegistrationForm(RecaptchaForm):
    '''Registration form for a new user
    '''
    username = forms.CharField(
        label = 'Nome de utilizador',
        required=True,
        max_length=30,)
    email = forms.EmailField(
        label = 'Email',
        required=False,
        help_text = 'Não é obrigatório')
    password_1 = forms.CharField(
        widget = forms.PasswordInput(render_value=False),
        label = 'Senha',
        required=True)
    password_2 = forms.CharField(
        widget = forms.PasswordInput(render_value=False),
        label = 'Confirmar senha',
        required=True)

    # The validation battery
    def clean_username(self):
        username = self.cleaned_data.get('username')
        for c in username:
            if c not in ALLOWEDCHARS:
                raise forms.ValidationError('O nome de utilizador não admite '
                    'espaços, ou caracteres com acentos.')
        return username

    def clean(self):
        cleaned_data = self.cleaned_data

        password_1 = cleaned_data.get('password_1')
        password_2 = cleaned_data.get('password_2')

        if not self._errors.has_key('password_2'):
            if password_1 != password_2:
                msg = u'As senhas não coincidem.'
                self._errors['password_2'] = ErrorList([msg])
            if len(password_1) < settings.PASSWORD_MIN_SIZE:
                msg = u'A senha é muito curta (minimo %s).' % settings.PASSWORD_MIN_SIZE
                self._errors['password_2'] = ErrorList([msg])
            if len(password_1) > settings.PASSWORD_MAX_SIZE:
                msg = u'A senha é muito longa (maximo %s).' % settings.PASSWORD_MAX_SIZE
                self._errors['password_2'] = ErrorList([msg])

        return cleaned_data

