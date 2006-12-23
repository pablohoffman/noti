from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core import urlresolvers
from django.http import QueryDict
import md5
import cfg

resolver = urlresolvers.RegexURLResolver(r'^/', 'urls')

# MANAGERS ------------------------------------------------------------------

class ArticleManager(models.Manager):
    def matching(self, site=None, category=None, tag=None, when=None, order=None, text=None, limit=cfg.query_max_articles):
        "Return articles that matches the given criteria"
        articles = self.get_query_set()

        if tag:
            if not isinstance(tag, Tag):
                tag = Tag.objects.get(id=tag)
            articles = tag.allarticles

        if site:
            if isinstance(site, Site):
                articles = articles.filter(category__site=site)
            else:
                articles = articles.filter(category__site__id=site)

        if category:
            if isinstance(category, Category):
                articles = articles.filter(category=category)
            else:
                articles = articles.filter(category__id=category)

        articles = when.filter(articles)

        if order == 'time':
            articles = articles.order_by('-datetime')
        else:
            articles = articles.order_by('-rank')

        if text:
            articles = articles.filter(Q(title__icontains=text) | Q(text__icontains=text))

        # always limit number of articles to fetch from db
        articles = articles[0:limit]

        return articles


class TagManager(models.Manager):
    def related(self, bykeyword=False, bycategory=False, when=None, limit=None):
        "Return all keyword/category tags with articles in the given range"
        tags = self.get_query_set()
        if not when:
            when = When()
        if bykeyword:
            return tags.filter(articles__datetime__range=(when.start, when.end)).distinct()
        if bycategory:
            return tags.filter(categories__articles__datetime__range=(when.start, when.end)).distinct()

    def catarticles(self, range='all', limit=None):
        "Return articles related to the given tag by its category, inside the given range"
        articles = Article.objects.all()
        

# MODELS --------------------------------------------------------------------

class Keyword(models.Model):
    name = models.CharField(maxlength=255, unique=True, db_index=True, default='')

    def _get_tags(self):
        return self.tag_set.all()
    tags = property(_get_tags)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Tag(models.Model):
    name = models.SlugField()
    keywords = models.ManyToManyField(Keyword, blank=True)

    def _get_allarticles(self):
        "returns all articles directly or indirectly (via category) related to this tag"
        return Article.objects.filter(Q(category__tags__id=self.id) | Q(tags__id=self.id)).distinct()
    allarticles = property(_get_allarticles)

    def _get_link(self):
        return '/' + resolver.reverse('notiuy.apps.noti.views.tag', self.name)
    link = property(_get_link)

    def get_absolute_url(self):
        return self.link   

    def __str__(self):
        return self.name

    def kwlist(self):
        return ' '.join([kw.name for kw in self.keywords.all()])
    kwlist.short_description = 'Keywords'

    class Admin:
        list_display = ['name', 'kwlist']

    objects = TagManager()


class Site(models.Model):
    name = models.CharField(maxlength=255)
    url = models.URLField()
    slug = models.SlugField(prepopulate_from=['name'])

    def _get_articles(self):
        return Article.objects.filter(category__site=self)
    articles = property(_get_articles)

    def save(self):
        if not self.slug: self.slug = slugify(self.name)
        super(Site, self).save()

    def _get_link(self):
        return '/' + resolver.reverse('notiuy.apps.noti.views.site', self.slug)
    link = property(_get_link)

    def get_absolute_url(self):
        return self.link   

    def __str__(self):
        return self.name

    class Admin:
        list_display = ('name', 'url')


class Category(models.Model):
    name = models.CharField(maxlength=255)
    site = models.ForeignKey(Site, related_name='categories')
    tags = models.ManyToManyField(Tag, related_name='categories')
    slug = models.SlugField(prepopulate_from=['name'])

    def __str__(self):
        return '%s - %s' % (self.site.name, self.name)

    def _get_link(self):
        return '/' + resolver.reverse('notiuy.apps.noti.views.category', self.site.slug, self.slug)
    link = property(_get_link)

    def get_absolute_url(self):
        return self.link   

    def save(self):
        if not self.slug: self.slug = slugify(self.name)
        super(Category, self).save()

    def taglist(self):
        return ' '.join([tag.name for tag in self.tags.all()])
    taglist.short_description = 'Tags'

    class Admin:
        list_display = ('name', 'site', 'taglist')


class Article(models.Model):
    datetime = models.DateTimeField()
    category = models.ForeignKey(Category, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles')
    title = models.CharField(maxlength=255, default='')
    url = models.URLField()
    text = models.TextField()
    rank = models.IntegerField(default=0)
    #image = models.FileField() # TODO: revisar cual es la mejor opcion para este campo
    hash = models.CharField(maxlength=32, unique=True, db_index=True, default='')

    def _get_site(self):
        return self.category.site
    site = property(_get_site)

    def _get_link(self, absolute=False):
        return '/' + resolver.reverse('notiuy.apps.noti.views.article', self.id) 
    link = property(_get_link)
    
    def _is_popular(self):
        return self.rank >= cfg.popular_threshold
    is_popular = property(_is_popular)

    def get_absolute_url(self):
        return self.link

    def _get_alltags(self):
        return Tag.objects.filter(Q(categories__id=self.category.id) | Q(articles__id=self.id)).distinct()
    alltags = property(_get_alltags)

    def makehash(self):
        self.hash = md5.new(self.url + self.title + self.text).hexdigest()
        
    def save(self):
        if not self.hash: self.makehash()
        super(Article, self).save()

    def __str__(self):
        return self.title

    class Admin:
        list_display = ('id', 'title', 'category', 'datetime')
        list_display_links = ('id', 'title')

    objects = ArticleManager()

class Favorite(models.Model):
    name = models.CharField(maxlength=255, default='', core=True)
    user = models.ForeignKey(User, related_name='favorites', edit_inline=models.TABULAR, core=True)
    path = models.CharField(maxlength=255, default='', core=True)
    slug = models.SlugField(prepopulate_from=['name'])

    def __str__(self):
        return self.name

    def _get_link(self):
        return '/' + resolver.reverse('notiuy.apps.noti.views.favorite', self.user.username, self.slug)
    link = property(_get_link)

    def _get_articles(self):
        path, query = self.path.split('?')
        view, args, kwargs = resolver.resolve(cfg.urlbase + path)
        articles = view(None, params=QueryDict(query), *args, **kwargs)
        return articles
    articles = property(_get_articles)

    def save(self):
        self.slug = slugify(self.name)
        super(Favorite, self).save()

    class Admin:
        pass

