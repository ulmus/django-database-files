from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control
import mimetypes
from database_files.models import File

@cache_control(max_age=86400)
def serve(request, file_id):
	f = get_object_or_404(File, pk=file_id)
	mimetype = mimetypes.guess_type(f.get_filename())[0] or 'application/octet-stream'
	response = HttpResponse(f.retreive(), mimetype=mimetype)
	response['Content-Length'] = f.size
	response['Content-Disposition'] = "filename=%s" % f.get_filename()
	return response
