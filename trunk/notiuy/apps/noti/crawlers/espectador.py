"""
Noti - Crawler for http://www.espectador.com
"""

from datetime import datetime, timedelta
from urllib import urlopen
from socket import timeout
import re
from notiuy.apps.noti.crawlers import NotiCrawler

class Crawler(NotiCrawler):
    siteslug = 'espectador'   
    sitename = 'Espectador'
    siteurl  = 'http://www.espectador.com'
    encoding = 'iso-8859-1'
    params   = []

    caturls = [
               ('Agro', 'http://www.espectador.com/area.php?idArea=1'),
               ('Cultura', 'http://www.espectador.com/area.php?idArea=2'),
               ('Deportes', 'http://www.espectador.com/area.php?idArea=3'),
               ('Politica', 'http://www.espectador.com/area.php?idArea=4'),
               ('Sociedad', 'http://www.espectador.com/area.php?idArea=5'),
               ('Economia', 'http://www.espectador.com/area.php?idArea=6'),
               ('Tecnologia', 'http://www.espectador.com/area.php?idArea=7'),
               ('Salud', 'http://www.espectador.com/area.php?idArea=15'),
               ('Tiempo libre', 'http://www.espectador.com/area.php?idArea=17'),
              ]

    def run(self):
        p = """
            (<span\sclass="texto">\s*(\d\d)\.(\d\d)\.(\d\d\d\d)|                                     # date   a[1] a[2] a[3]
             (\d?\d):\s?(\d\d)(\shs)?<).*?                                                           # time   a[4] a[5]
            (<a\shref="(/_dyn/mediaNode/go.php\?[^"]*id=\d+)"\sclass="titulo2?"\s*>|                 # link1  a[8]
             <a\shref="(/_dyn/mediaNode/go.php\?[^"]*id=\d+)">\s*<span\sclass="ed_ant_tit_nota">)    # link2  a[9]
            ([^<]*)<.*?                                                                              # title  a[10]
            <span\sclass="texto">\s*([^<]+)<                                                         # text   a[11]
        """
        r = re.compile(p, re.VERBOSE | re.DOTALL)

        for cat, url in self.caturls:
            try:
                page = urlopen(url).read()
                # get rid of annoying tags that confuses the parser
                page = re.sub(r'<(/?b|/?i|/?strong|/?em|br ?/?)>', '', page)
            except timeout:  # espectador.com gives a lot of socket timeout errors, so we ignore them
                continue

            for a in r.findall(page):
                now = datetime.now()
                if a[1]:
                    dt = now.replace(int(a[3]), int(a[2]), int(a[1]))
                if a[4]:
                    dt = now.replace(hour=int(a[4]), minute=int(a[5]))
                    if dt > now:
                        dt = dt - timedelta(1)
                link = a[8] or a[9]
                self.addarticle(title=a[10],
                                url=self.siteurl + link,
                                text=a[11],
                                datetime=dt,
                                category=cat,
                               )
