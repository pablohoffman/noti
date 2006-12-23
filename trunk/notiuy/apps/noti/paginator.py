import cfg

class ArticlePaginator:
    def __init__(self, request, articles):
        """
        * Generates multi-page results object which are later rendered in template: boxes/pager.html
        * Return the slice of articles associated with the current page

        Properties:
        - needed: True if pagination is needed
        - articles: articles on current page
        - total: total number of pagse
        - pages: list of page dicts containing the following keys:
            - number: page number
            - active: True if this is the active page
            - link: link to this page
        """

        max = cfg.articles_per_page

        # accesing the  _limit private attribute is the only way to find out if 
        # the QuerySet has been sliced, but we check first if it exists to provide
        # a failsafe alternative
        if hasattr(articles, '_limit') and articles._limit:
            limit = articles._limit
            c = min(articles.count(), limit)
        else:
            c = articles.count()

        if (c > max): 
            p = int(request.GET.get('p') or '1')
            t = min((c-1) / max + 1, cfg.max_pages)
            q = request.GET.copy()

            self.needed = True
            self.pages = []
            for i in range(1, t+1):
                q['p'] = i
                self.pages.append({'number': i, 'active': i==p, 'link': '%s?%s' % (request.path, q.urlencode())})
            self.total = c
            self.articles = articles[(p-1)*max:p*max]
        else:
            self.needed = False
            self.articles = articles
