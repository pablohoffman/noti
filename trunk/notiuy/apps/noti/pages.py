from times import When

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import feedgenerator

from sidebar import SubscribeBox
from paginator import ArticlePaginator
from urls import uri
import cfg

class SimplePage(object):
    def __init__(self, request, nav, title, **kwargs):
        self.request = request
        self.nav = nav
        self.title = title

        for k, v in kwargs.iteritems():
            setattr(self, k, v) 

    def get(self, key, default=None):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        else:
            return default

    def uri(self):
        return uri(self.request.path)

    def render(self, tpl='base.html', **kwargs):
        if 'err' in self.request.session:
            self.err = self.request.session['err']
            del(self.request.session['err'])
        elif 'msg' in self.request.session:
            self.msg = self.request.session['msg']
            del(self.request.session['msg'])

        args = {'cfg': cfg, 'page': self}
        args.update(kwargs)
        return render_to_response(tpl, RequestContext(self.request, args))


class NewsPage(SimplePage):
    sections = []

    def __init__(self, request, nav, title, when=None, **kwargs):
        self.request = request
        self.nav = nav

        super(NewsPage, self).__init__(request, nav, title, **kwargs)
        self.sections = []
        self.sidebar = []
        self.subs = None
        self.when = when or When()

        self._title = self.title
        self.title = '%s, %s' % (title, self.when.label)

        if not self.when.archived and not self.get('nosubs', False):
            addfav=self.get('addfav', True)
            self.subs = SubscribeBox(request, self.title, addfav=addfav)

        if self.nav != 'search':
            request.session['backtitle'] = self.title
            request.session['backurl'] = request.path

        if request.GET.has_key('o'):
            request.session['o'] = request.GET['o']

    def addsection(self, articles, **kwargs):
        section = kwargs
        section['articles'] = articles
        section['more'] = articles.count() >= cfg.section_max_articles
        self.sections.append(section)
    
    def _get_multisection(self):
        return len(self.sections) > 1
    multisection = property(_get_multisection)

    def paginate(self):
        self.paginator = ArticlePaginator(self.request, self.sections[0]['articles'])
        self.sections[0]['articles'] = self.paginator.articles
    
    def customsearch(self, key, val):
        self.search = {'key': key, 'val': val}
        self.search['label'] = _('Search in %s') % self._title

    def render(self, tpl='news.html'):
        if self.request.GET.get('f') in ['rss2', 'atom']:
            return self.feed(self.request.GET['f'])

        if 'err' in self.request.session:
            self.err = self.request.session['err']
            del(self.request.session['err'])
        elif 'msg' in self.request.session:
            self.msg = self.request.session['msg']
            del(self.request.session['msg'])

        if self.sections and not self.multisection:
            self.paginate()

        return render_to_response(tpl, RequestContext(self.request, {'cfg': cfg, 'page': self}))

    def feed(self, format):
        if format=='atom':
            feed = getattr(feedgenerator, 'Atom1Feed')
        if format=='rss2':
            feed = getattr(feedgenerator, 'Rss201rev2Feed')
        f = feed(
            title=unicode('%s - %s' % (cfg.sitename, self.title), 'utf8'),
            link=unicode(self.uri(), 'utf8'),
            description=unicode(cfg.sitename, 'utf8'),
            language=unicode('en', 'utf8'),
            feed_url=unicode(self.uri(), 'utf8'),
            )

        for article in self.sections[0]['articles']:
            f.add_item(
                title=unicode(article.title, 'utf8'),
                link=unicode(uri(article.link), 'utf8'),
                description=unicode(article.text, 'utf8'),
                pubdate=article.datetime,
                categories=[unicode(tag.name, 'utf8') for tag in article.alltags]
                )
        
        return HttpResponse(f.writeString('utf8'), mimetype='text/xml')
