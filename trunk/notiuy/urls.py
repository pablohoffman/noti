from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^', include('notiuy.apps.noti.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
    # For development only
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': '/opt/notiuy/media'}),
)
