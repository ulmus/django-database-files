from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<file_id>\d+)$', 'database_files.views.serve', name='database_file'),
)
