from database_files import models
from django.core.files.storage import Storage
from django.core.urlresolvers import reverse
from django.conf import settings

DATABASE_FILES_COMPRESSION = settings.get("DATABASE_FILES_COMPRESSION", False)

class DatabaseStorage(Storage):

	def __init__(self, encryption=False, compression=False):
		compression = DATABASE_FILES_COMPRESSION or compression
		encryption = DATABASE_FILES_ENCRYPTION or encryption
		super(DatabaseStorage, self).__init__()

	def _generate_name(self, name, pk):
		"""
		Replaces the filename with the specified pk
		"""
		return '%s' % pk

	def _open(self, name, mode='rb'):
		try:
			f = models.File.objects.get(pk=name)
		except models.File.DoesNotExist:
			return None
		return f.retreive()

	def _save(self, name, content):
		f = models.File.objects.create(
				file_name = name,
				)
		f.store(content)
		return self._generate_name(name, f.pk)

	def exists(self, name):
		return models.File.objects.filter(pk=name).exists()

	def delete(self, name):
		try:
			models.File.objects.get(pk=name).delete()
		except models.File.DoesNotExist:
			pass

	def url(self, name):
		return reverse('database_file', kwargs={'name': name})

	def size(self, name):
		try:
			return models.File.objects.get(pk=name).size
		except models.File.DoesNotExist:
			return 0

	def modified_time(self, name):
		try:
			return models.File.objects.get(pk=name).modified_time
		except models.File.DoesNotExist:
			return None

	def accessed_time(self, name):
		try:
			return models.File.objects.get(pk=name).accessed_time
		except models.File.DoesNotExist:
			return None

	def created_time(self, name):
		try:
			return models.File.objects.get(pk=name).created_time
		except models.File.DoesNotExist:
			return None
