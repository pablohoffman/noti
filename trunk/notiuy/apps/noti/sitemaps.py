from django.contrib.sitemaps import Sitemap
from models import Site, Category, Tag

import cfg

class SiteSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Site.objects.all()

class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Category.objects.all()

class TagSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Tag.objects.all()
    
class PopularSitemap(Sitemap):
    priority = 0.8

    def items(self):
        return ['', 'lastweek', 'lastmonth', 'lastyear', 'all']

    def location(self, rangesuf):
        return '%s/popular/%s/' % (cfg.urlbase, rangesuf)

    def changefreq(self, rangesuf):
        return {'':          'daily',
                'lastweek':  'daily',
                'lastmonth': 'weekly',
                'lastyear':  'weekly',
                'all':       'weekly',
               }[rangesuf]
        if rangesuf == '' or rangesuf == 'lastweek':
            return 'daily'
        if rangesuf == 'lastmonth':
            return 'weekly'
        if rangesuf == 'lastyear':
            return 'weekly'

    def priority(self, rangesuf):
        return {'':          0.8,
                'lastweek':  0.6,
                'lastmonth': 0.6,
                'lastyear':  0.6,
                'all':       0.8,
               }[rangesuf]
    
class SpecificSitemap(Sitemap):
    def __init__(self, path, prio=0.7, freq='daily'):
        self.location = cfg.urlbase + path
        self.changefreq = freq
        self.priority = prio

    def items(self):
        return [self]
