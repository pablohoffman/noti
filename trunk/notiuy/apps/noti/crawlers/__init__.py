import socket
from datetime import datetime, date
import htmlentitydefs
import re

from noti.models import Article, Site, Category, Tag, Keyword
from noti.utils.httppost import post_multipart
from noti import cfg, version

sep = '-' * 78 + "\n"

def buildtagre():
    tagre = []
    for tag in Tag.objects.filter(keywords__isnull=False).distinct():
        kws = [kw.name for kw in tag.keywords.all()]
        restr = '(' + '|'.join(kws) + ')'
        tagre.append((tag, re.compile(restr, re.IGNORECASE)))
    return tagre


def tag(article, tagre, test=False, reset=False):
    """ populate article with keyword-tags. returns list of tag names applied """

    if reset and not test: 
        article.tags.clear()
    txt = article.title + article.text
    tags = []
    for tag, regex in tagre:
        if regex.search(txt):
            tags.append(tag.name)
            if not test: 
                article.tags.add(tag)
    return tags


def crawl(crawlers, opt):
    socket.setdefaulttimeout(cfg.timeout)

    if opt.date:
        dt = date(int(opt.date[0:4]), int(opt.date[4:6]), int(opt.date[6:8]))
    else:
        dt = None

    print "Noti %s crawler" % version
    print "Crawling: %s" % ' '.join(crawlers)
    if opt.date:
        print "    Date: %s\n" % dt.strftime('%d-%m-%Y %H:%M')

    for cr in crawlers:
        try:
            __import__(cr, globals(), locals())
        except ImportError:
            print sep, "ERROR: no such crawler '%s'\n" % cr, sep
            continue
        mod = globals()[cr]
        Crawler = getattr(mod, 'Crawler')

        failed = 1
        i = 0
        #while failed and i <= cfg.retries:
            #try:
        try:
            print "\n%s: starting crawler\n" % cr, sep,
            c = Crawler(debug=opt.verbose, test=opt.test, date=dt)
            c.run()
            print sep, "%s: finished. %s articles fetched (%s new, %s dupes)" % (cr, c.count, c.added, c.dupes)
        except NotImplementedError, msg:
            print "ERROR[%s]: %s" % (cr, msg)
        failed = 0
                    
            #except:
                #failed = 1

            #if failed:
                #i += 1
                #if i <= cfg.retries:
                    #print "ERROR: %s. Retrying..." % errstr
                #else:
                    #print "ERROR: %s. Given up. Sorry." % errstr

def retag(dates, opt):
    if not dates:
        dates = [datetime.now().strftime('%Y%m%d')]

    tagre = buildtagre()
    for d in dates:
        for article in Article.objects.matching(year=d[0:4], month=d[4:6], day=d[6:8]):
            tags = tag(article, tagre, opt.test, opt.reset)
            if opt.verbose or tags:
                print "%s | %s" % (article.category, article.title)
            if tags:
                print "### TAGS:", ' '.join(tags)


class NotiCrawler(object):
    "Noti base crawler class"
    
    def __init__(self, debug=0, test=False, date=None):
        self.debug = debug
        self.test = test
        self.count = self.added = self.dupes = 0
        self.datetime = datetime.now()
        self.tagre = buildtagre()
        if date:
            if 'date' in self.params:
                self.datetime = self.datetime.replace(date.year, date.month, date.day)
            else:
                raise NotImplementedError, "does not support date parameter"

    def _converthtmlentity(self, m):
        if m.group(1)=='#':
            try:
                return chr(int(m.group(2)))
            except ValueError:
                return '.%s;' % m.group(2)
        else:
            try:
                return unicode(htmlentitydefs.entitydefs[m.group(2)], 'iso-8859-1').encode('utf-8')
            except KeyError:
                return '&%s;' % m.group(2)

    # remove HTML entities from the given string
    def htmlclean(self, str):
        return re.sub(r'&(#?)(.+?);', self._converthtmlentity, str)

    # Overridable -- parse news
    def run(self):
        raise NotImplementedError

    def addarticle(self, **data):
        data['category'] = data.get('category') or self.category
        data['datetime'] = data.get('datetime') or datetime.now()
        data['text'] = data.get('text') or ''
        for k in ['title', 'text']:  # all text fields should go here
            if self.encoding != 'utf-8':
                data[k] = unicode(data.get(k), self.encoding).encode('utf-8')
            data[k] = data[k].replace("\n", " ").replace("\r", " ")
            data[k] = self.htmlclean(data[k])

        # assign site/category (create them if not exists)
        site = Site.objects.get_or_create(slug=self.siteslug, defaults={'name': self.sitename, 'url': self.siteurl})[0]
        data['category'] = Category.objects.get_or_create(site=site, name=data['category'], defaults={'site': site})[0]

        article = Article(**data)
        article.makehash()
        exists = Article.objects.filter(hash=article.hash).count()

        self.count += 1
        if exists:
            print "DUPE[%s]: %s" % (article.category.name, article)
            self.dupes += 1
        else:
            if self.test:
                print "-test- ADDED[%s]: %s" % (article.category.name, article)
                self.added += 1
            else:
                article.save()
                print "ADDED[%s]: %s" % (article.category.name, article)
                self.added += 1

        if self.debug == 2: 
            print article.__dict__

        if not exists:
            tags = tag(article, self.tagre, self.test)
            if self.debug and tags:
                print "### TAGS:", ' '.join(tags)
