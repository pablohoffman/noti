"""
Noti - crawler for http://www.montevideo.com.uy
"""

from datetime import datetime
from notiuy.apps.noti.utils import feedparser
from notiuy.apps.noti.crawlers import NotiCrawler

class Crawler(NotiCrawler):
    siteslug = 'montevideo-comm'
    sitename = 'Montevideo COMM'
    siteurl  = 'http://www.montevideo.com.uy'
    encoding = 'utf-8'
    params   = []

    urls = ['http://www.montevideo.com.uy/anxml.cgi?58',
            'http://www.montevideo.com.uy/anxml.cgi?59',
            'http://www.montevideo.com.uy/anxml.cgi?60' ]

    def run(self):
        for url in self.urls:
            if self.debug: print 'RSS2> %s' % url
            d = feedparser.parse(url)
            for e in d.entries:
                d, m, y = e.updated.encode('utf-8').split('.')
                self.addarticle(title=e.title.encode('utf-8'),
                                datetime=datetime.now().replace(int(y), int(m), int(d)),
                                category=e.category.encode('utf-8'),
                                url=e.link.encode('utf-8'),
                                text=e.description.encode('utf-8')
                               )

