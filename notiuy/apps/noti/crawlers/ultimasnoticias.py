"""
Noti: crawler for http://www.utlimasnoticias.com.uy
"""

from urllib import urlopen
import re
from notiuy.apps.noti.crawlers import NotiCrawler

class Crawler(NotiCrawler):
    siteslug = 'ultimas-noticias'
    sitename = 'Ultimas Noticias'
    siteurl  = 'http://www.ultimasnoticias.com.uy'
    encoding = 'iso-8859-1'
    params   = ['date']

    caturls = [
               ('General', 'http://www.ultimasnoticias.com.uy/hemeroteca/%s/portada/general.html', 'act\d\d\.html'),
               ('Agro', 'http://www.ultimasnoticias.com.uy/hemeroteca/%s/portada/agro.html', 'agro\d\d\.html'),
               ('Economia', 'http://www.ultimasnoticias.com.uy/hemeroteca/%s/portada/economia.html', 'eco\d\d\.html'),
               ('Policiales', 'http://www.ultimasnoticias.com.uy/hemeroteca/%s/portada/policiales.html', 'poli\d\d\.html'),
               ('Internacionales', 'http://www.ultimasnoticias.com.uy/hemeroteca/%s/portada/internacional.html', 'int\d\d\.html'),
               ('Deportes', 'http://www.ultimasnoticias.com.uy/hemeroteca/%s/portada/deportes.html', 'dep\d\d\.html'),
              ]

    def run(self):
        dtstr = self.datetime.strftime('%d%m%y')

        for cat, url, pat in self.caturls:
            p = """
                (prints/%s).*?                               # link   a[0]
                javascript:">([^<]+)</a>.*?                  # title  a[1]
                <span\sclass="copete1">\s*(\w[^<]+)</span>   # text a[2]
            """ % pat
            r = re.compile(p, re.VERBOSE | re.DOTALL)

            url = url % dtstr
            page = urlopen(url).read()

            # cleanup
            page = re.sub(r'<(/?b|/?i|/?strong|/?em|br ?/?)>', '', page)
            page = re.sub(r'[\n\r]', '', page)
            page = re.sub(r'  *', ' ', page)

            for a in r.findall(page):
                self.addarticle(title=a[1],
                                datetime=self.datetime,
                                url='%s/hemeroteca/%s/prints/%s' % (self.siteurl, dtstr, a[0]),
                                text=a[2],
                                category=cat,
                               )
