from datetime import datetime, date, timedelta
from django.http import QueryDict
from urls import link
from times import When
import re
import cfg


class DayNav:
    def __init__(self, module, when, title=_('This week')):
        pl = link(module)

        self.title = title
        self.links = [{'url': pl + date.today().strftime('%Y-%m-%d/'), 'label': _('Today'), 'selected': when.date==date.today()}]
        dt = datetime.now()
        td = timedelta(1)
        for i in range(1, 7):
            dt -= td
            self.links.append({'url': pl + dt.strftime('%Y-%m-%d/'), 'label': dt.strftime('%A %d'), 'selected': when.date==dt.date()})


class RangeNav:
    def __init__ (self, module, when, title=_('Range')):
        if not when: 
            when = When()

        pl = link(module)

        self.title = title
        self.links = [{'url': pl, 'label': _('Last 24 hs'), 'selected': when.range=='today'},
                      {'url': pl + 'lastweek/', 'label': _('Last week'), 'selected': when.range=='week'},
                      {'url': pl + 'lastmonth/', 'label': _('Last month'), 'selected': when.range=='month'},
                      {'url': pl + 'lastyear/', 'label': _('Last year'), 'selected': when.range=='year'},
                      {'url': pl + 'all/', 'label': _('All'), 'selected': when.range=='all'},
                     ]


class OrderNav:
    def __init__(self, request, title=_('Order')):
        o = request.session.get('o', 'rank')
        
        self.title = title
        self.links = [{'url': '%s?o=rank' % request.path, 'label': _('Most popular first'), 'selected': o=='rank'},
                      {'url': '%s?o=time' % request.path, 'label': _('Latest first'), 'selected': o=='time'},]


class ObjectNav:
    def __init__(self, objects, when=None, title='', selected_id=-1):
        if not when:
            when = When()
        self.title = title
        self.links = []
        for object in objects:
            self.links.append({'url': when.object_link(object), 'label': object.name, 'selected': object.id==selected_id})


class SubscribeBox:
    def __init__(self, request, name='', addfav=True):
        "returns links for available subscription formats unless disabled evaluates to True"
        q = QueryDict('').copy()
        for k in ['o']:
            if request.session.get(k):
                q[k] = request.session[k]

        q2 = QueryDict('').copy()
        q2['name'] = name
        q2['path'] = '%s?%s' % (request.path[len(cfg.urlbase):], q.urlencode())
        if addfav: 
            self.add = '%s/addfavorite/?%s' % (cfg.urlbase, q2.urlencode())
        q['f'] = 'rss2'
        self.rss2 = '%s?%s' % (request.path, q.urlencode())
        q['f'] = 'atom'
        self.atom = '%s?%s' % (request.path, q.urlencode())

