import locale
from notiuy import settings

class NotiMiddleware(object):
    "This middleware takes care of commons tasks to all Noti pages"

    def process_request(self, request):
        locale.setlocale(locale.LC_TIME, settings.LANGUAGE_CODE)
        if request.session.get('msienew'):
            request.session['msienew'] = False
        if not request.session.get('cssfile'):
            msie = request.META.get('HTTP_USER_AGENT').find('MSIE') >= 0
            if msie:
                css = 'styles_ie.css'
            else:
                css = 'styles.css'
            request.session['msie'] = msie
            request.session['msienew'] = msie
            request.session['cssfile'] = css
