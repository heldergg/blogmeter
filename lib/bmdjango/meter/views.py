# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from meter.models import Blog, Stats

PAGE_DISPLAY = 25

def result(request, dt):
    context = {}

    objects = Stats.objects.filter(date__exact = dt ).order_by(
        '-visits_daily_average',
        '-visits_total',
        '-pages_daily_average',
        '-pages_total')
    paginator = Paginator(objects, PAGE_DISPLAY)

    page = request.GET.get('page', 1)
    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)

    context['page'] = stats 
    context['update_time'] = settings.CHANGE_DAY

    return render_to_response('results.html', context,
                context_instance=RequestContext(request))
    
def current_result(request):
    if settings.CHANGE_DAY > datetime.now().time():
        # Show yesterday data:
        return result(request, (datetime.now() - timedelta(1)).date() )
    else:    
        return result(request, date.today())
