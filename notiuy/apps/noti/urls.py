from django.conf.urls.defaults import *
from sitemaps import SiteSitemap, CategorySitemap, TagSitemap, PopularSitemap, SpecificSitemap
import cfg

sitemaps = {
    'sites': SpecificSitemap('/sites/', prio=0.8),
    'site': SiteSitemap,
    'category': CategorySitemap,
    'tags': SpecificSitemap('/tags/', prio=0.8),
    'tag': TagSitemap,
    'popular': PopularSitemap,
    'help': SpecificSitemap('/help/', prio=0.8, freq='weekly'),
    'about': SpecificSitemap('/about/', prio=0.8, freq='weekly'),
}

urlpatterns = patterns('notiuy.apps.noti.views',
    (r'^$', 'popular'),
    (r'^popular/(?P<when>[^/]*)/$', 'popular'),
    (r'^popular/$', 'popular'),
    (r'^sites/(?P<when>[^/]*)/$', 'sites'),
    (r'^sites/$', 'sites'),
    (r'^site/(?P<site>[\w-]+)/(?P<category>[\w-]+)/(?P<when>[^/]*)/$', 'category'),
    # note: possible collision with category/site url
    (r'^site/(?P<site>[\w-]+)/(?P<when>(last[^/]+|all|\d\d\d\d-\d\d-\d\d))/$', 'site'), 
    (r'^site/(?P<site>[\w-]+)/(?P<category>[\w-]+)/$', 'category'),
    (r'^site/(?P<site>[\w-]+)/$', 'site'),
    (r'^tags/(?P<when>[^/]*)/$', 'tags'),
    (r'^tags/$', 'tags'),
    (r'^tag/(?P<tag>[\w-]+)/(?P<when>[^/]*)/$', 'tag'),
    (r'^tag/(?P<tag>[\w-]+)/$', 'tag'),
    (r'^user/(?P<user>[\w-]+)/$', 'user'),
    (r'^user/(?P<user>[\w-]+)/(?P<fav>[\w-]+)/$', 'favorite'),

    (r'^search/$', 'search'),
    (r'^article/(?P<id>\d+)/$', 'article'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^register/$', 'register'),
    (r'^profile/$', 'profile'),
    (r'^addfavorite/$', 'addfavorite'),

    (r'^about/$', 'about'),
    (r'^help/$', 'help'),
)

urlpatterns += patterns('',
    # Google sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)

def link(module=None):
    "Returns URL path for given module (can be object or string)"
    if isinstance(module, str):
        return '%s/%s/' % (cfg.urlbase, module)
    else:
        return module.link

def uri(path):
    "Returns URI for given path"
    return 'http://' + cfg.httphost + path

