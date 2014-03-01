# -*- coding: utf-8 -*-

# Global imports:
from django import forms

class AddBlogForm(forms.Form):
    """
    Form used to add a blog to the blogometer
    """
    url = forms.CharField(
        label = 'URL blog',
        required=True,
        max_length=1000,)
