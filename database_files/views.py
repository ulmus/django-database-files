from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control
import mimetypes
from database_files.models import DatabaseFile

@cache_control(max_age=86400)
def serve(request, file_id):
	f = get_object_or_404(DatabaseFile, pk=file_id)
	safe_filename = f.get_filename()
	try:
		import unidecode
		safe_filename = unidecode.unidecode(safe_filename)
	except ImportError:
		pass
	mimetype = mimetypes.guess_type(safe_filename)[0] or 'application/octet-stream'
	response = HttpResponse(f.retreive(), mimetype=mimetype)
	response['Content-Length'] = f.size
	response['Content-Disposition'] = "attachment; filename=%s" % safe_filename
	return response
