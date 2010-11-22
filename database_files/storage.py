from database_files import models
from database_files.module_settings import DBF_SETTINGS
from django.core.files.storage import Storage
from django.core.urlresolvers import reverse
from django.conf import settings

class DatabaseStorage(Storage):

	def _generate_name(self, pk):
		"""
		Replaces the filename with the specified pk
		"""
		return str(pk)

	def _open(self, name, mode='rb'):
		try:
			f = models.DatabaseFile.objects.get(pk=name)
		except models.DatabaseFile.DoesNotExist:
			return None
		return f.retreive()

	def _save(self, name, content):
		f = models.DatabaseFile.objects.create(
				filepath=name,
				)
		f.store(content,
				encrypt=DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"],
				compress=DBF_SETTINGS["DATABASE_FILES_COMPRESSION"],
				)
		return self._generate_name(f.pk)

	def exists(self, name):
		return False
		# return models.File.objects.filter(filepath=name).exists()

	def delete(self, name):
		try:
			models.DatabaseFile.objects.get(pk=name).delete()
		except models.DatabaseFile.DoesNotExist:
			pass

	def url(self, name):
		return reverse('database_file', kwargs={'name': name})

	def size(self, name):
		try:
			return models.DatabaseFile.objects.get(pk=name).size
		except models.DatabaseFile.DoesNotExist:
			return 0

	def modified_time(self, name):
		try:
			return models.DatabaseFile.objects.get(pk=name).modified_time
		except models.DatabaseFile.DoesNotExist:
			return None

	def accessed_time(self, name):
		try:
			return models.DatabaseFile.objects.get(pk=name).accessed_time
		except models.DatabaseFile.DoesNotExist:
			return None

	def created_time(self, name):
		try:
			return models.DatabaseFile.objects.get(pk=name).created_time
		except models.DatabaseFile.DoesNotExist:
			return None
