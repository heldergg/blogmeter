# -*- coding: utf-8 -*-

'''
This module contains the necessary tools to crawl the sitemeter.com site and
extract the blog stats for the blogmeter project.
'''

# Imports

import bs4
import logging
import os.path
import socket
import sys
import unicodedata
import urllib
import re

# Append the current project path
sys.path.append(os.path.abspath('../lib/'))
sys.path.append(os.path.abspath('../lib/bmdjango/'))

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Socket timeout in seconds
socket.setdefaulttimeout(60)

# Import the django models
from meter.models import Blog
from django.db.utils import IntegrityError


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

##
## Add new blog
##

# http://s10.sitemeter.com/stats.asp?site=s10448000
sitemeter_re = r'http://[a-zA-Z0-9\-_]+\.sitemeter.com/(?:stats.asp|js/counter\.js)\?site=(?P<sitemeter_key>[a-zA-Z0-9]+)'


class AddBlog(object):
    def __init__(self, url):
        self.url = url


    def run(self):
        print '* Getting page: ', self.url
        html = urllib.urlopen(self.url).read()
        soup = bs4.BeautifulSoup(html)

        name = soup.title.renderContents().strip()
        print '  Blog name: ', name


        sitemeter_key = re.findall(sitemeter_re, html)
        if len(sitemeter_key) > 1:
            print '  Multi sitemeter keys, aborting!'
            sys.exit(1)

        elif len(sitemeter_key) == 0:
            print '  Didn\'t find a sitemeter key, aborting!'
            print '''
Não encontrei a chave do sitemeter no seu blog. Antes de pudermos
inscrever o blog no Blogómetro é necessário conseguirmos ler as
respectivas estatísticas. Leia por favor o nosso FAQ:

http://blogometro.aventar.eu/faq/

E certifique-se que reune as condições necessárias.

Se já se inscreveu no sitemer certifique-se que coloca o respectivo
código no seu blog. Pode encontrar na web instruções para configurar
o site meter para a sua plataforma, por exemplo:

* Blogspot:

http://www.sitemeter.com/flash/installation/blogger/blogspot_video.html

* Wordpress:

http://support.sitemeter.com/index.php?_m=knowledgebase&_a=viewarticle&kbarticleid=155


/Helder
            '''
            sys.exit(1)

        sitemeter_key = sitemeter_key[0]

        print '  Sitemeter key: ', sitemeter_key

        blog = Blog(
            name = name,
            url  = self.url,
            sitemeter_key = sitemeter_key )

        try:
            blog.save()
        except IntegrityError:
            print '  Duplicated sitemer key, aborting!'
            sys.exit(1)

        print '  Success! Added "%s" blog to the database.' % name
        print '  Statistics URL: http://blogometro.aventar.eu/mt/info/%d/' % blog.id

        from webscraper.scrapstats import SitemeterScraper

        scraper = SitemeterScraper()
        scraper.read_blog(sitemeter_key)
