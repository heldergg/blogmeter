# -*- coding: utf-8 -*-

'''
This module contains the necessary tools to crawl the sitemeter.com site and
extract the blog stats for the blogmeter project.
'''

# Imports

import bs4
import logging
import os.path
import random
import socket
import sys
import time
import traceback
import unicodedata
import urllib

from datetime import date, datetime, timedelta

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

def debug_unicode( st ):
    if isinstance( st, unicode):
        return unicodedata.normalize('NFKD', st).encode('ascii','ignore')
    else:
        return unicodedata.normalize('NFKD', unicode( st, 'ascii', 'ignore')).encode('ascii')
du = debug_unicode

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
        print '* Getting stats for: %s' % du(self.blog.name)
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

    def check_stat(self, blog):
        '''Returns True if we have read the blog stats today
        '''
        try:
            Stats.objects.get( blog = blog, date = date.today() )
            print "  Already got today's stats."
            return True
        except ObjectDoesNotExist:    
            return False

    def read_blog(self, sitemeter_key ):
        try:
            blog = Blog.objects.get( sitemeter_key = sitemeter_key )
            if self.check_stat( blog ):
                print "* ERROR: We have read this blog's stats today, bailing out."
                return
        except ObjectDoesNotExist:
            print "* ERROR: Sorry, we don't have %s key in our db." % sitemeter_key
            return

        try:
            stats = UpdateStats(blog).run()
            # Reset the read error count
            blog.error_count = 0
            blog.save()
            print "* Success!"
            return stats
        except socket.timeout:
            # There was a timeout
            print "* ERROR: There was a time out maybe the server is busy, try again later"
        except Exception, msg:
            # Uncaught error
            print "* ERROR: %s" % msg


    def run(self):
        blog_list = list(self.blog_list)
        while blog_list:
            blog = blog_list.pop()

            # Take the stat once per day
            if self.check_stat(blog):
                continue

            # Sleep for a little bit if the last stat read was less than
            # 5 minutes ago.
            if (datetime.now() - blog.last_try) < timedelta(0, 5 * 60):
                print '  Read this stat less than 5 minutes ago. Sleeping a bit'
                time.sleep(60)

            # Read the blog stats
            try:
                stats = UpdateStats(blog).run()
                # Reset the read error count
                blog.error_count = 0
            except (socket.timeout, IndexError) as e:
                # Recoverable error, going to try again
                blog_list.insert(0, blog)
                print '  Returned the blog to the queue.'
            except Exception, msg:
                # Increase the blog's error count
                blog.error_count = blog.error_count + 1
                print msg

                # Print the error traceback (for debugging):
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                tb = traceback.format_exc()
                print tb
            finally:    
                blog.last_try = datetime.now()    
                blog.save()
                                    
            t = 0.5
            print '  Sleeping %4.2f seconds' % t
            time.sleep(t)
