import locale
from notiuy import settings

class NotiMiddleware(object):
    "This middleware takes care of commons tasks to al Noti pages"

    def process_request(self, request):
        locale.setlocale(locale.LC_TIME, settings.LANGUAGE_CODE)
