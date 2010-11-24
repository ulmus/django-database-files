from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.core import files
from django.core.cache import cache
from database_files.exceptions import DatabaseFilesEncryptionError
from database_files.module_settings import DBF_SETTINGS
import base64
import zlib
import random
import binascii
import os
import string
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist



# Use cStringIO if available, for performance
from django.db.models import permalink

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

try:
	from Crypto.Cipher import AES
except ImportError:
	pass
else:
	if settings.SECRET_KEY:
		cipher = AES.new(settings.SECRET_KEY[:32])


class DatabaseFileStore(models.Model):
	"""
	The content is set in another model to avoid loading it prematurely if it was cached
	"""
	content = models.TextField(blank=True, null=True)

class DatabaseFile(models.Model):
	filestore = models.OneToOneField("DatabaseFileStore", blank=True, null=True)
	filepath = models.TextField(max_length=250, blank=True, null=True)
	size = models.IntegerField(blank=True, null=True)
	encrypted = models.BooleanField(default=False, editable=False)
	compressed = models.BooleanField(default=False, editable=False)
	created_time = models.DateTimeField(auto_now_add=True)
	modified_time = models.DateTimeField(auto_now=True)
	accessed_time = models.DateTimeField(auto_now_add=True)
	padding_length = models.SmallIntegerField(default=0)

	@permalink
	def get_absolute_url(self):
		return ('database_file', [str(self.id)])

	def store(self, file, encrypt=False, compress=False):
		"""
		Stores a file into the database object
		file = The file that should be stored, should be a python file-like object
		encrypt = Set to true if the file should be encrypted, requires Crypto.Cipher to be installed,
		otherwise it does nothing
		compress = compress the file using zlib compression
		"""
		estring = file.read()
		self.size = file.size
		self.filepath = file.name

		if DBF_SETTINGS["DATABASE_FILES_CACHE"] and DBF_SETTINGS["DATABASE_FILES_CACHE_UNENCRYPTED"]:
			# Pre-fill the cache, the reasoning being that the file will probably be needed
			# immediately after storing
			cache.set(self.get_cache_key(), estring)

		if compress:
			# Compress using zlib, this should be done before encryption
			if not self.get_extension() in DBF_SETTINGS["DATABASE_FILES_COMPRESSION_EXCLUDE"]:
				estring = zlib.compress(estring)
				self.compressed = True

		if encrypt and cipher and DBF_SETTINGS["DATABASE_FILES_SECRET_KEY"]:
			estring = self._encrypt_string(estring)
			self.encrypted = True

		estring = self._encode_string(estring)
		self._store_string(estring)

		if DBF_SETTINGS["DATABASE_FILES_CACHE"] and not DBF_SETTINGS["DATABASE_FILES_CACHE_UNENCRYPTED"]:
			# Pre-fill the cache,
			cache.set(self.get_cache_key(), estring)

		self.save()

	def _store_string(self, estring):
		if self.filestore:
			self.filestore.delete()
		filestore = DatabaseFileStore(content=estring.encode("utf-8"))
		filestore.save()
		self.filestore = filestore
		self.save()

	def _retreive_string(self):
		if self.filestore:
			return unicode(self.filestore.content)
		else:
			return ""

	def retreive(self, mode="rb"):
		"""
		Constructs and returns a django file object from content
		"""
		if DBF_SETTINGS["DATABASE_FILES_CACHE"]:
			estring = cache.get(self.get_cache_key())
			if not estring:
				estring = self._decode_string(self._retreive_string())
				if not DBF_SETTINGS["DATABASE_FILES_CACHE_UNENCRYPTED"]:
					estring = self._process_string(estring)
				cache.set(self.get_cache_key(), estring)
			else:
				estring = self._decode_string(self._retreive_string())
				estring = self._process_string(estring)
		else:
			estring = self._retreive_string()
			estring = self._decode_string(estring)
			estring = self._process_string(estring)

		string_file = StringIO(estring)
		django_file = DFile(string_file)
		django_file.db_filename = self.filepath
		django_file.name = self.filepath
		django_file.mode = mode
		django_file.size = self.size
		django_file.url = self.get_absolute_url()

		self.accessed_time = datetime.now()
		self.save()
		return django_file

	def get_raw_string(self):
		# Mainly meant for testing
		return self._retreive_string()

	def get_decoded_string(self):
		# Mainly meant for testing
		estring = self._retreive_string()
		estring = self._decode_string(estring)
		return estring

	def _decode_string(self, estring):
		return base64.b64decode(estring)

	def _encode_string(self, estring):
		return base64.b64encode(estring)

	def _encrypt_string(self, estring):
		# Encrypt using the AES algorithm and the site's Secret Key
		padding = cipher.block_size - len(estring) % cipher.block_size
		if padding and padding < cipher.block_size:
			estring += ''.join([random.choice(string.printable) for index in range(padding)])
			self.padding_length = padding
			self.save()
		return cipher.encrypt(estring)

	def _decrypt_string(self, estring):
		if not cipher:
			raise DatabaseFilesEncryptionError("Trying to decrypt file '%s', encryption module not found" % self.filepath)
		if not DBF_SETTINGS["DATABASE_FILES_SECRET_KEY"]:
			raise DatabaseFilesEncryptionError("Trying to decrypt file '%s', neither SECRET_KEY nor DATABASE_FILES_SECRET_KEY set." % self.filepath)
		return cipher.decrypt(estring)[:len(estring) - self.padding_length]

	def _process_string(self, estring):
		if self.encrypted:
			estring = self._decrypt_string(estring)
		if self.compressed:
			estring = zlib.decompress(estring)
		return estring

	def get_filename(self):
		dir_name, file_name = os.path.split(self.filepath)
		return file_name

	def get_path(self):
		dir_name, file_name = os.path.split(self.filepath)
		return dir_name

	def get_extension(self):
		filename = self.get_filename()
		file_root, file_ext = os.path.splitext(filename)
		return file_ext

	def get_fileroot(self):
		filename = self.get_filename()
		file_root, file_ext = os.path.splitext(filename)
		return file_root

	def get_cache_key(self):
		return "DJANGO-DATABASE_FILE-%s" % self.pk

class DFile(files.File):
	db_filename = ""
