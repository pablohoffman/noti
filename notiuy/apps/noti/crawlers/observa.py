"""
Noti - Crawler for http://observa.com.uy
"""

from datetime import datetime
from urllib import urlopen
import re
from notiuy.apps.noti.crawlers import NotiCrawler

class Crawler(NotiCrawler):
    siteslug = 'observa'
    sitename = 'Observa'
    siteurl  = 'http://www.observa.com.uy'
    encoding = 'utf-8'
    params   = []

    caturls = [('Actualidad', 'http://www.observa.com.uy/Osecciones/actualidad/default.aspx?seccion=actualidad'),
               ('Economia', 'http://www.observa.com.uy/Osecciones/economia/default.aspx?seccion=economia'),
               ('Ciencia', 'http://www.observa.com.uy/Osecciones/ciencia/default.aspx?seccion=ciencia'),
               ('Vida', 'http://www.observa.com.uy/Osecciones/vida/default.aspx?seccion=vida'),
               ('Deportes', 'http://www.observa.com.uy/Osecciones/deportes/default.aspx?seccion=deportes')]

    def run(self):
        for cat, url in self.caturls:
            p = """
                <a[^>]*href="(/Osecciones/%s/nota.aspx\?id=\d+)">   # link   a[0]
                ([^<]*)</a>                                         # title  a[1]
                \s*</h\d>\s*
                (<p>([^<]*)</p>|<[^p])                              # text   a[2]
            """ % cat.lower()
            r = re.compile(p, re.VERBOSE | re.DOTALL)

            page = urlopen(url).read()
            for a in r.findall(page):
                self.addarticle(title=a[1],
                                datetime=datetime.now(),
                                url=self.siteurl + a[0],
                                text=a[2],
                                category=cat,
                               )
