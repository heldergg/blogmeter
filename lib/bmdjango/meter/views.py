# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import calendar
import urllib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

from meter.models import Blog, Stats
from meter.forms import AddBlogForm
from webscraper.utils import AddBlog,UtilsError

PAGE_DISPLAY = 30
FIRSTYEAR = 2012

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
## Monthly stats
##

def current_month(request):
    dt = date.today()
    month = dt.month
    year = dt.year
    return redirect(reverse('monthly_stats',kwargs={'year':year, 'month':month}))

def aggregate_month(request):
    dt = date.today()
    month = dt.month
    year = dt.year
    return redirect(reverse('aggregate_stats',kwargs={'year':year, 'month':month}))

month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

def month_delta( year, month, delta ):
    if delta not in (-1, 1):
        raise Exception('delta must be -1 or 1')
    month = month + delta
    if month > 12:
        month = 1
        year += 1
    if month < 1:
        month = 12
        year -= 1
    return year, month

def month_url( year, month):
    url = reverse('monthly_stats',kwargs={'year':year, 'month':month})
    text = '%s/%d' % (month_names[month-1], year)

    return { 'text': text, 'month': month, 'year':year }

def next_month_url( year, month):
    year, month =  month_delta( year, month, 1)
    return month_url(year, month)

def prev_month_url( year, month):
    year, month = month_delta( year, month, -1)
    return month_url(year, month)

def monthly_view(request, template, year, month, query):
    context = {}

    # Args checking
    try:
        year = int(year)
        cmonth = int(month)
    except:
        raise Http404
    if cmonth<1 or cmonth>12:
        raise Http404
    try:
        highlight = int(request.GET.get('highlight', -1))
    except:
        highlight = -1

    # Utilities
    context['month'] = month_names[cmonth-1]
    context['year'] = year
    context['next_month'] = next_month_url( year, cmonth )
    context['prev_month'] = prev_month_url( year, cmonth )
    context['highlight'] = highlight

    # Find the boundary dates
    initial_date = date(year, cmonth, 1)
    final_date = date(year,cmonth,calendar.monthrange(year,cmonth)[1])

    # Get the data:
    objects = Blog.objects.raw(query, [initial_date, final_date])
    context['objects'] = objects
    context['start_date'] = initial_date
    context['end_date'] = final_date

    # Pagination
    paginator = Paginator(list(objects), PAGE_DISPLAY)
    page = request.GET.get('page', 1)
    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)
    context['page'] = stats

    return render_to_response(template, context,
                context_instance=RequestContext(request))

## Monthly stats
def monthly_stats(request, year, month):
    query = '''select
           b.id,
           b.name as name,
           b.url as url,
           b.sitemeter_key as sitemeter_key,
           sum(s.visits_daily_average) as visits,
           sum(s.pages_daily_average) as pages,
           1.0*sum(s.pages_daily_average)/sum(s.visits_daily_average) as quality
       from
           meter_blog b,
           meter_stats s
       where
           s.date >= %s and
           s.date <= %s and
           b.id = s.blog_id
       group by
           b.id
       order by
           sum(s.visits_daily_average) desc;'''
    return monthly_view(request, 'monthly_stats.html', year, month, query )

## Stats over a period of time
def stats_period(request, dt0, dt1):
    context = {}

    # Get the dates:
    try:
        initial_date = datetime.strptime(dt0, '%Y-%m-%d').date()
        final_date = datetime.strptime(dt1, '%Y-%m-%d').date()
    except:
        raise Http404

    if initial_date > final_date:
        print "#" * 80
        initial_date, final_date = final_date, initial_date

    # Query
    query = '''select
           b.id,
           b.name as name,
           b.url as url,
           b.sitemeter_key as sitemeter_key,
           sum(s.visits_daily_average) as visits,
           sum(s.pages_daily_average) as pages,
           1.0*sum(s.pages_daily_average)/sum(s.visits_daily_average) as quality
       from
           meter_blog b,
           meter_stats s
       where
           s.date >= %s and
           s.date <= %s and
           b.id = s.blog_id
       group by
           b.id
       order by
           sum(s.visits_daily_average) desc;'''

    # Get the data:
    objects = Blog.objects.raw(query, [initial_date, final_date])
    context['objects'] = objects
    context['start_date'] = initial_date
    context['end_date'] = final_date

    # Pagination
    paginator = Paginator(list(objects), PAGE_DISPLAY)
    page = request.GET.get('page', 1)
    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)
    context['page'] = stats

    return render_to_response('stats_period.html', context,
                context_instance=RequestContext(request))

## Aggregate stats
def aggregate_stats(request, year, month):
    query = '''select
            id,
            date,
            sum(visits_daily_average) as visits,
            sum(pages_daily_average) as pages
        from
            meter_stats
        where
            date >= %s and
            date <= %s
        group by
            date;
    '''
    return monthly_view(request, 'aggregate_stats.html', year, month, query)

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

##
## Admin views
##

@login_required
def blog_add(request):
    context = {}
    context.update(csrf(request))
    context['success'] = False
    message = ''

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        form = AddBlogForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            add_tool = AddBlog(url)
            try:
                message = add_tool.run()
                context['success'] = True
                form = AddBlogForm()
            except UtilsError,e:
                message = e.msg
    else:
        form = AddBlogForm()

    context['form'] = form
    context['message'] = message

    return render_to_response('blog_add.html', context,
                context_instance=RequestContext(request))
