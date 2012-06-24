# -*- coding: utf-8 -*-

'''
This module contains the necessary tools to crawl the sitemeter.com site and
extract the blog stats for the blogmeter project.
'''

# Imports

import sys
import logging
import os.path
import urllib
import bs4
import random
import time
import traceback
import socket

from datetime import date

# Django general
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Append the current project path
sys.path.append(os.path.abspath('../lib/'))
sys.path.append(os.path.abspath('../lib/bmdjango/'))

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Socket timeout in seconds
socket.setdefaulttimeout(60)

# Import the django models
from meter.models import Blog, Stats


##
## Utils
##


def get_int( st ):
    if st.strip() == '-': return 0
    return int(st.replace(',',''))

def get_float( st ):
    if st.strip() == '-': return 0
    return float(st.replace(',',''))

def get_time( st ):
    if st.strip() == '-': return 0
    mm, ss = [ int(xi) for xi in st.split(':') ]
    return 60 * mm + ss


class UpdateStats(object):
    def __init__(self, blog):
        self.blog = blog

    def get_raw(self, soup):
        # The nearest common element sequence
        stats_table = soup.find('table', { 'id':'Table_02' } ).contents[7
                        ].contents[3].contents[3].contents[1
                        ].contents[3].contents[1].contents
        # Unparsed list of visit stats                
        visits_stats = [ stats_table[i].contents[2].font.renderContents() 
                           for i in range(4,10) ]
        # Unparsed list of page views stats                   
        stats_pages = [ stats_table[i].contents[2].font.renderContents()
                            for i in range(13,19) ]

        return visits_stats + stats_pages                    

    def parse(self, raw_result):
        result = {}
        result['visits_total'] = get_int(raw_result[0])
        result['visits_daily_average'] = get_int(raw_result[1])
        result['visits_lenght_average'] = get_time(raw_result[2])
        result['visits_last_hour'] = get_int(raw_result[3])
        result['visits_today'] = get_int(raw_result[4])
        result['visits_this_week'] = get_int(raw_result[5])
        result['pages_total'] = get_int(raw_result[6])
        result['pages_daily_average'] = get_int(raw_result[7])
        result['pages_visit_average'] = get_float(raw_result[8]) 
        result['pages_last_hour'] = get_int(raw_result[9])
        result['pages_today'] = get_int(raw_result[10])
        result['pages_this_week'] = get_int(raw_result[11])

        return result

    def save_reading(self, result):
        stats = Stats()

        stats.blog = self.blog 

        stats.visits_total            = result['visits_total']
        stats.visits_daily_average    = result['visits_daily_average'] 
        stats.visits_lenght_average   = result['visits_lenght_average']
        stats.visits_last_hour        = result['visits_last_hour']
        stats.visits_today            = result['visits_today']
        stats.visits_this_week        = result['visits_this_week']
        stats.pages_total             = result['pages_total']
        stats.pages_daily_average     = result['pages_daily_average']
        stats.pages_visit_average    = result['pages_visit_average']
        stats.pages_last_hour         = result['pages_last_hour']
        stats.pages_today             = result['pages_today']
        stats.pages_this_week         = result['pages_this_week']

        stats.save() 

    def run(self):
        print '* Getting stats for: %s' % self.blog.name
        print '  %s' % self.blog.sitemeter_url()

        html = urllib.urlopen(self.blog.sitemeter_url()).read()
        soup = bs4.BeautifulSoup(html)
        raw_result = self.get_raw(soup)
        parsed_result = self.parse(raw_result)

        self.save_reading(parsed_result) 

MAXBLOGERROR = 5

class SitemeterScraper(object):
    def __init__(self):
        self.blog_list = Blog.objects.filter(error_count__lt = MAXBLOGERROR )

    def run(self):
        for blog in self.blog_list:
            try:
                Stats.objects.get( blog = blog, date = date.today() )
                print "  Already got today's stats."
            except ObjectDoesNotExist:
                try:
                    stats = UpdateStats(blog).run()
                except Exception, msg:
                    # TODO: should not use a catch all except
                    #
                    # timeout should not increase the error_count
                    #
                    blog.error_count = blog.error_count + 1
                    blog.save()

                    print 
                    print msg
                    print 

                    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                    tb = traceback.format_exc()
                    print tb
                                    
                t = 0.5
                print '  Sleeping %d seconds' % t
                time.sleep(t)
