from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Q
from models import Article, Tag, Site, Category, Favorite
from paginator import ArticlePaginator
from times import When
from urls import link
from sidebar import DayNav, RangeNav, ObjectNav, OrderNav, SubscribeBox 
from pages import SimplePage, NewsPage
from manipulators import RegisterManipulator, ProfileManipulator, FavoriteManipulator

import cfg


def getarg(key, request, params):
    if request:
        return request.GET.get('o') or request.session.get('o')
    else:
        return params.get('o')


def login(request):
    page = SimplePage(request, 'login', _('Login'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(link('user/%s' % user.username))
        else:
            page.err = _('User does not exist or wrong password')

    return page.render('login.html')


def register(request):
    manipulator = RegisterManipulator()
    page = SimplePage(request, 'register', _('New user'))

    if request.method == 'POST':
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            new_user = manipulator.save(new_data)
            page.msg = _('New user created succesfully. You may login now.')
            return page.render()
        else:
            page.err = _('Some errors were found processing your request. Please verify.')
    else:
        errors = new_data = {}

    form = forms.FormWrapper(manipulator, new_data, errors)
    return page.render('register.html', form=form)


def profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(link('login'))

    manipulator = ProfileManipulator(request.user.id)
    page = SimplePage(request, 'profile', _('User profile'))

    if request.method == 'POST':
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            new_user = manipulator.save(new_data)
            request.session['msg'] = _("Profile changes saved")
            return HttpResponseRedirect(link('user/%s' % request.user.username))
    else:
        errors = {}
        new_data = manipulator.flatten_data()

    form = forms.FormWrapper(manipulator, new_data, errors)
    return page.render('profile.html', form=form)


def addfavorite(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(link('login'))

    manipulator = FavoriteManipulator(request.user.id)
    page = SimplePage(request, 'addfav', _('Add to favorites'))
    if request.POST:
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            new_user = manipulator.save(new_data)
            return HttpResponseRedirect(link('user/%s' % request.user.username))
    else:
        errors = {}
        new_data = {'name': request.GET.get('name'), 'path': request.GET.get('path')}

    form = forms.FormWrapper(manipulator, new_data, errors)
    return page.render('addfavorite.html', form=form, path=new_data['path'])


def category(request, site, category, when='', params=None):
    order = getarg('o', request, params)
    when = When(when)
    category = Site.objects.get(slug=site).categories.get(slug=category)
    articles = Article.objects.matching(category=category, when=when, order=order)
    if not request: return articles

    page = NewsPage(request, 'category', str(category), when)
    page.sidebar.append(ObjectNav(Site.objects.all(), when, _('Sites'), category.site.id))
    page.sidebar.append(ObjectNav(category.site.categories.all(), when, _('%s categories') % category.site.name, category.id))
    page.sidebar.append(OrderNav(request))
    page.sidebar.append(RangeNav(category, when))
    page.sidebar.append(DayNav(category, when))
    page.addsection(articles)
    page.customsearch('c', category.id)

    return page.render()


def site(request, site, when='', params=None):
    order = getarg('o', request, params)
    when = When(when)
    site = Site.objects.get(slug=site)
    articles = Article.objects.matching(site=site, when=when, order=order)
    if not request: return articles

    page = NewsPage(request, 'site', site.name, when)
    page.sidebar.append(ObjectNav(Site.objects.all(), when, _('Sites'), site.id))
    page.sidebar.append(ObjectNav(site.categories.all(), when, _('%s categories') % site.name))
    page.sidebar.append(OrderNav(request))
    page.sidebar.append(RangeNav(site, when))
    page.sidebar.append(DayNav(site, when))
    page.addsection(articles)
    page.customsearch('s', site.id)

    return page.render()


def tag(request, tag, when='', params=None):
    order = getarg('o', request, params)
    when = When(when)
    tag = Tag.objects.get(name=tag)
    articles = Article.objects.matching(tag=tag, when=when, order=order)
    if not request: return articles

    page = NewsPage(request, 'tag', tag.name, when)
    page.sidebar.append(OrderNav(request))
    page.sidebar.append(RangeNav(tag, when))
    page.sidebar.append(DayNav(tag, when))
    page.addsection(articles)
    page.customsearch('t', tag.id)

    return page.render()


def tags(request, when=''):
    when = When(when)
    ctags = Tag.objects.related(bycategory=True, when=when)
    ktags = Tag.objects.related(bykeyword=True, when=when)

    if ctags:
        for tag in ctags:
            articles = when.filter(Article.objects.all())
            tag.quant = articles.filter(category__tags__id=tag.id).count()
        ctotal = max(max([tag.quant for tag in ctags]), 1) or 1
        for tag in ctags:
            tag.size = max(tag.quant * cfg.tagcloud_maxsize / ctotal, cfg.tagcloud_minsize)
            tag.linkwhen = when.object_link(tag)
    
    if ktags:
        for tag in ktags:
            articles = when.filter(Article.objects.all())
            tag.quant = articles.filter(tags__id=tag.id).count()
        ktotal = max(max([tag.quant for tag in ktags]), 1) or 1
        for tag in ktags:
            tag.size = max(tag.quant * cfg.tagcloud_maxsize / ktotal, cfg.tagcloud_minsize)
            tag.linkwhen = when.object_link(tag)

    page = NewsPage(request, 'tag', _('Tags'), when, nosubs=True)
    page.sidebar.append(RangeNav('tags', when))
    page.sidebar.append(DayNav('tags', when))
    page.ctags = ctags
    page.ktags = ktags
    
    return page.render('tags.html')


def sites(request, when='', params=None):
    order = getarg('o', request, params)
    when = When(when)
    sites = Site.objects.all()

    if order=='time':
        title = _('Latest news by site')
    else:
        title = _('Most viewed news by site')

    page = NewsPage(request, 'site', title, when, nosubs=True)
    page.sidebar.append(ObjectNav(Site.objects.all(), when, _('Sites')))
    page.sidebar.append(RangeNav('sites', when))
    page.sidebar.append(DayNav('sites', when))
    for site in sites:
        articles = Article.objects.matching(site=site, when=when, order=order, limit=cfg.section_max_articles)
        page.addsection(articles, name=site.name, link=when.object_link(site)) 
    
    return page.render()
    

def popular(request, when='', params=None):
    order = getarg('o', request, params)
    when = When(when)
    articles = Article.objects.matching(when=when, order=order, limit=cfg.popular_max_articles)
    if not request: return articles

    page = NewsPage(request, 'popular', _('Most popular news'), when)
    page.sidebar.append(RangeNav('popular', when))
    page.sidebar.append(DayNav('popular', when))
    page.addsection(articles)

    return page.render()


def search(request):
    when = When(request.GET.get('r'))
    q = request.GET.get('q')
    g = request.GET
    articles = Article.objects.matching(site=g.get('s'), category=g.get('c'), tag=g.get('t'), when=when, text=q, limit=cfg.search_max_articles)
    
    title = _('Search results for "%(query)s"') % {'query': q}
    page = NewsPage(request, 'search', title, when)
    page.addsection(articles)
    page.q  = q

    if 'backtitle' in request.session:
        page.back = {'link': request.session.get('backurl'), 'label': request.session.get('backtitle')}

    return page.render()


def user(request, user):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(link('login'))
    if user != request.user.username:
        return HttpResponseRedirect(link('login'))

    title = _('%(user)s favorites') % {'user': user}
    page = NewsPage(request, 'user', title, When(), addfav=False)
    page.sidebar.append(ObjectNav(request.user.favorites.order_by('slug'), When(), _('Favorites')))
    page.nosections = _("You don't have any favorites")
    for fav in request.user.favorites.all():
        articles = fav.articles[0:cfg.section_max_articles]
        page.addsection(articles, name=fav.name, link=fav.link) 

    return page.render()


def favorite(request, user, fav):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(link('login'))
    if user != request.user.username:
        return HttpResponseRedirect(link('login'))

    favs = request.user.favorites
    fav = favs.get(slug=fav)
    articles = fav.articles[0:cfg.section_max_articles]

    title = '%s: %s' % (user, fav.name)
    page = NewsPage(request, 'user', title, When(), addfav=False)
    page.sidebar.append(ObjectNav(favs.order_by('slug'), When(), _('Favorites'), fav.id))
    page.addsection(articles)

    return page.render()


def article(request, id):
    article = Article.objects.get(id=id)
    article.rank += 1
    article.save()
    return HttpResponseRedirect(article.url)


def logout(request):
    request.session['msg'] = _("You have been logged out")
    auth.logout(request)
    return HttpResponseRedirect(link('sites'))


def help(request):
    page = SimplePage(request, 'help', _('Frequently asked questions'))
    page.sites = Site.objects.all()
    return page.render('help.html')


def about(request):
    page = SimplePage(request, 'about', _('About %(site)s') % {'site': cfg.sitename})
    return page.render('about.html')
