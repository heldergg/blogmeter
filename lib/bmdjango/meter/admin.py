# -*- coding: utf-8 -*-

from django.contrib import admin
from meter.models import Blog

class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sitemeter_key', 'error_count') 
    ordering = ('name',)
    search_fields = ('name', 'url', 'sitemeter_key')
admin.site.register(Blog, BlogAdmin)
