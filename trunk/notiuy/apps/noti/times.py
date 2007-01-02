from datetime import datetime, date, timedelta
import re

class When:
    "Class which represents an abstract time range for displaying articles"

    dtre = re.compile(r'^(\d\d\d\d)-?(\d\d)-?(\d\d)$')
    labels = {'today': _('last 24 hs'),
              'week': _('last week'),
              'month': _('last month'),
              'year': _('last year'),
              'all': _('all times'),}
    days = {'today': 1, 'week':  7, 'month': 31, 'year':  365}

    def __init__(self, whenstr=''):
        self.range = self.year = self.month = self.day = self.label = ''
        self.date = None
        self.slug = whenstr
        self.archived = False
        self.start = None
        self.end = datetime.now()
        if not whenstr or whenstr=='today':
            self.range = 'today'
            self.label = 'last 24 hs'
            self.start = datetime.now().replace(hour=0, minute=0, second=0)
        elif whenstr == 'all':
            self.range = 'all'
            self.label = 'all times'
            self.start = datetime.min
            self.end = datetime.now()
        elif whenstr[0:4] == 'last':
            self.range = whenstr[4:]
            self.label = self.labels[self.range]
            self.start = datetime.now() - timedelta(self.days[self.range])
        else:
            m = self.dtre.match(whenstr)
            self.archived = True
            if m:
                self.year, self.month, self.day = m.groups()
                self.date = date(int(self.year), int(self.month), int(self.day))
                self.label = self.date.strftime('%d %b %Y')
                self.start = datetime(self.date.year, self.date.month, self.date.day)
                self.end = self.start + timedelta(1)

    def object_link(self, object):
        return object.link + self.slug

    def filter(self, articles):
        "Apply the datetime period defined by this class to the given articles QuerySet"
        if self.range == 'all':
            return articles
        else:
            return articles.filter(datetime__range=(self.start, self.end))


