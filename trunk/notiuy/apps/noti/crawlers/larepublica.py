"""
Noti - Crawler for http://www.larepublica.com.uy
"""

import re
from datetime import date, datetime
from urllib import urlopen
from noti.crawlers import NotiCrawler

import sys

class Crawler(NotiCrawler):
    siteslug = 'la-republica'   
    sitename = 'La Republica'
    siteurl  = 'http://www.larepublica.com.uy'
    encoding = 'iso-8859-1'
    params   = []

    caturls = [
        ('Politica', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=907'),
        ('Economia', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=904'),
        ('Editorial', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=905'),
        ('Justicia', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=906'),
        ('Mundo', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=913'),
        ('Deportes', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=903'),
        ('Comunidad', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=902'),
        ('Cultura', 'http://www.larepublica.com.uy/lr3/?a=seccion&s=901'),
    ]
        
    def run(self):
        p = r"""
            <a\shref="([^>]*a=nota[^>]*)        # link   a[0]
            (\d{4})-(\d{2})-(\d{2})[^>]*">      # date   a[1] a[2] a[3]
            ([^<]*)</a>                         # title  a[4]
            (\s*?<span[^>]*>([^<]*)</span>)?    # text   a[6]
            \s*</li>
        """
        r = re.compile(p, re.VERBOSE | re.DOTALL)

        for cat, url in self.caturls:
            page = urlopen(url).read()
            for a in r.findall(page):
                self.addarticle(title=a[4],
                                datetime=datetime.now().replace(int(a[1]), int(a[2]), int(a[3])),
                                url=self.siteurl + '/lr3/' + a[0],
                                text=a[6],
                                category=cat,
                               )
