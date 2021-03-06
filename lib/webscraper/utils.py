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

# Errors
class UtilsError(Exception):
    def __init__(self, expr, msg=None):
        self.expr = expr
        self.msg = msg


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
        logger.info('ADD BLOG %s' % self.url)
        message = u''
        message += u'  Ler página do blog: %s\n' % self.url
        html = urllib.urlopen(self.url).read()
        soup = bs4.BeautifulSoup(html)

        name =  unicode(soup.title.renderContents().strip(), 'utf-8')
        message += u'  Nome do blog: %s\n' % name


        sitemeter_key = re.findall(sitemeter_re, html)
        sitemeter_key = list(set(sitemeter_key))
        if len(sitemeter_key) > 1:
            message += u'  Multi sitemeter keys, aborting!'
            raise UtilsError('Multi sitemeter keys, aborting!', message)

        elif len(sitemeter_key) == 0:
            logger.info('No Sitemeter key for %s' % self.url)
            message += u'  Não encontrei a chave do sitemeter. Vou desistir.\n'
            message += u'''
Pode enviar a seguinte mensagem a quem tentou inscrever o blog:

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

/Aventar
            '''
            raise UtilsError('Didn\'t find a sitemeter key, aborting!', message)

        sitemeter_key = sitemeter_key[0]

        message += u'  Chave do sitemeter: %s\n' % sitemeter_key

        blog = Blog(
            name = name,
            url  = self.url,
            sitemeter_key = sitemeter_key )

        try:
            blog.save()
        except IntegrityError:
            logger.info('Duplicated Sitemeter key for %s' % self.url)
            message += u'  Chave do sitemeter duplicada na base de dados, vou desistir!'
            raise UtilsError(u'Duplicated sitemer key, aborting!', message)

        message +=  u'  Sucesso, adicionei o blog "%s" à base de dados.\n' % name
        message +=  u'  URL das estatísticas: http://blogometro.aventar.eu/mt/info/%d/' % blog.id

        from webscraper.scrapstats import SitemeterScraper

        scraper = SitemeterScraper()
        try:
            stats = scraper.read_blog(sitemeter_key)
        except AttributeError:
            stats = None

        if stats:
            logger.info('Success %s' % self.url)
            message +=  u'''
Pode enviar a seguinte mensagem a quem tentou inscrever o blog:

ASSUNTO: Blogómetro - %(blog_name)s

Feito!

Pode consultar as estatísticas do blog em:

http://blogometro.aventar.eu/mt/info/%(blog_id)s/

/Aventar
''' % { 'blog_id': blog.id, 'blog_name': name }
        else:
            logger.info('Could not get stats %s' % self.url)
            message +=  u'''
Pode enviar a seguinte mensagem a quem tentou inscrever o blog:

ASSUNTO: Blogómetro - %(blog_name)s

Inscrição feita, mas não conseguimos ler as suas estatísticas,
veja por favor o nosso FAQ:

    http://blogometro.aventar.eu/faq/

As suas estatísticas irão aparecer em:

    http://blogometro.aventar.eu/mt/info/%(blog_id)s/

Se não resolver o problema em 10 dias desistimos de tentar ler as
suas estatísticas. Se isso acontecer, basta mandar-me um mail para
eu fazer a activação.

/Aventar
''' % { 'blog_id': blog.id, 'blog_name': name }

        return message
