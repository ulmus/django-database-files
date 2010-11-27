from database_files import models
from database_files.module_settings import DBF_SETTINGS
from django.core.files.storage import Storage
from django.core.urlresolvers import reverse
from django.conf import settings

class DatabaseStorage(Storage):

	def __init__(self, encrypt=DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"], compress=DBF_SETTINGS["DATABASE_FILES_COMPRESSION"], *args, **kwargs):
		self.encrypt = encrypt
		self.compress = compress
		super(DatabaseStorage, self).__init__(*args, **kwargs)

	def _open(self, name, mode='rb'):
		try:
			f = models.DatabaseFile.objects.get(filepath=name)
		except models.DatabaseFile.DoesNotExist:
			return None
		return f.retreive()

	def _save(self, name, content):
		f = models.DatabaseFile.objects.create(
				filepath=name,
				)
		f.store(content,
				encrypt=self.encrypt,
				compress=self.compress,
				)
		return name

	def exists(self, name):
		return models.DatabaseFile.objects.filter(filepath=name).exists()

	def delete(self, name):
		try:
			models.DatabaseFile.objects.get(filepath=name).delete()
		except models.DatabaseFile.DoesNotExist:
			pass

	def url(self, name):
		try:
			file = models.DatabaseFile.objects.get(filepath=name)
		except models.DatabaseFile.DoesNotExist:
			return None
		return reverse('database_file', kwargs={'file_id': file.pk})

	def size(self, name):
		try:
			return models.DatabaseFile.objects.get(filepath=name).size
		except models.DatabaseFile.DoesNotExist:
			return 0

	def modified_time(self, name):
		try:
			return models.DatabaseFile.objects.get(filepath=name).modified_time
		except models.DatabaseFile.DoesNotExist:
			return None

	def accessed_time(self, name):
		try:
			return models.DatabaseFile.objects.get(filepath=name).accessed_time
		except models.DatabaseFile.DoesNotExist:
			return None

	def created_time(self, name):
		try:
			return models.DatabaseFile.objects.get(filepath=name).created_time
		except models.DatabaseFile.DoesNotExist:
			return None
