"""
Noti: Crawler for www.elpais.com.uy
"""

from datetime import date
from notiuy.noti.utils import feedparser
from notiuy.noti.crawlers import NotiCrawler

class Crawler(NotiCrawler):
    siteslug = 'el-pais'
    sitename = 'El Pais'
    siteurl  = 'http://www.elpais.com.uy'
    encoding = 'utf-8'
    params   = []

    caturls = [('Editorial', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=editorial'),
               ('Nacional', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=nacional'),
               ('Ciudades', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=ciudades'),
               ('Internacional', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=internacional'),
               ('Economia', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=economia'),
               ('Deportes', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=deportes'),
               ('Espectaculos', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=espectaculos'),
               ('Ultimo momento', 'http://www.elpais.com.uy/formatos/rss/index.asp?seccion=ultmom')
              ]

    def run(self):
        for cat, url in self.caturls:
            if self.debug: print 'RSS2> %s' % url
            d = feedparser.parse(url)
            for e in d.entries:
                self.addarticle(title=e.title.encode('utf-8'),
                                category=cat,
                                url=e.link.encode('utf-8'),
                                text=e.description.encode('utf-8')
                               )
