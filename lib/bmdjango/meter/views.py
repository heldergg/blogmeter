# -*- coding: utf-8 -*-

from datetime import date

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Max
from django.core.paginator import Paginator

from meter.models import Blog, Stats

def result(request, dt):
    context = {}

    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except:
        page = 1

    objects = Stats.objects.filter(date__exact = dt ).order_by('-visits_daily_average')
    paginator = Paginator(objects, 25)

    if page < 1:
        page = 1
    if page > paginator.num_pages:
        page = paginator.num_pages

    context['page'] = paginator.page(page)


    return render_to_response('results.html', context,
                context_instance=RequestContext(request))
    
def current_result(request):
    return result(request, date.today())
