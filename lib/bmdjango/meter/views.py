# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import urllib

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from meter.models import Blog, Stats

PAGE_DISPLAY = 25

##
## Result display
##

def result(request, dt):
    context = {}

    objects = Stats.objects.filter(date__exact = dt ).order_by(
        '-visits_daily_average',
        '-visits_total',
        '-pages_daily_average',
        '-pages_total')
    paginator = Paginator(objects, PAGE_DISPLAY)

    # GET arguments
    page = request.GET.get('page', 1)
    try:
        highlight = int(request.GET.get('highlight', -1))
    except:
        highlight = -1

    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)

    context['highlight'] = highlight
    context['page'] = stats 
    context['update_time'] = settings.CHANGE_DAY
    context['today'] = dt
    context['yesterday'] = (dt - timedelta(1))
    if dt < date.today():
        context['tomorrow'] = (dt + timedelta(1))

    return render_to_response('results.html', context,
                context_instance=RequestContext(request))
    
def current_result(request):
    if settings.CHANGE_DAY > datetime.now().time():
        # Show yesterday data:
        return result(request, (datetime.now() - timedelta(1)).date() )
    else:    
        return result(request, date.today())

def result_archive(request, dt):
    try:
        dt =  datetime.strptime(dt,'%Y-%m-%d').date()
    except ValueError:
        raise Http404
    return result(request, dt)

def blog_highlight(request, dt, blog_id):                
    context = {}

    # Check the URL:
    try:
        dt =  datetime.strptime(dt,'%Y-%m-%d').date()
    except ValueError:
        raise Http404

    blog = get_object_or_404(Blog, id = blog_id )
        
    # Get the blog classification
    objects = Stats.objects.filter(date__exact = dt ).order_by(
        '-visits_daily_average',
        '-visits_total',
        '-pages_daily_average',
        '-pages_total').values_list('blog_id', flat=True)

    have_classification = False
    for index, blog_id in enumerate(objects):    
        if blog_id == blog.id:
            have_classification = True
            break

    if not have_classification:
        context['blog'] = blog
        context['date'] = dt
        return render_to_response('no_classification.html', context,
               context_instance=RequestContext(request))
      
    # Calculate the page number:
    page_number = index / PAGE_DISPLAY + 1 

    return redirect('%s?page=%d&highlight=%d' % (reverse('result_archive', kwargs={'dt':dt}),
                                    page_number,
                                    blog.id))

def highlight_today(request, blog_id):
    blog = get_object_or_404(Blog, id = blog_id )
    if settings.CHANGE_DAY > datetime.now().time():
        # Show yesterday data:
        return blog_highlight(request, (datetime.now() - timedelta(1)).date().isoformat(), blog.id )
    else:    
        return blog_highlight(request, date.today().isoformat(), blog.id )
##
## Blog search
##

def blog_search(request):
    context = {}

    query = request.GET.get('query','').strip()
    if len(query) > 128:
        raise Http404

    # NOTE: If the number of blogs grows substantially (tens of thousands)
    # this search method has to be changed.
    result = Blog.objects.filter( Q(name__icontains = query) |
                                 Q(sitemeter_key__icontains = query) |
                                 Q(url__icontains = query) 
                               ).order_by('name')

    paginator = Paginator(result, PAGE_DISPLAY)

    page = request.GET.get('page', 1)
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)

    context['page'] = blogs
    context['query'] = urllib.quote(query.encode('utf8'))

    return render_to_response('blog_list.html', context,
                context_instance=RequestContext(request))

def blog_info(request, blog_id):
    context = {}

    blog = get_object_or_404(Blog, id = blog_id )
        
    objects = Stats.objects.filter(blog__exact = blog ).order_by( '-date' )
    paginator = Paginator(objects, PAGE_DISPLAY)

    page = request.GET.get('page', 1)
    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)

    context['page'] = stats
    context['blog'] = blog

    return render_to_response('blog_info.html', context,
                context_instance=RequestContext(request))

           
           
