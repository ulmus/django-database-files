from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.core import files
from django.core.cache import cache
from database_files.exceptions import DatabaseFilesEncryptionError
import base64
import zlib
import random
import binascii
import os
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

DATABASE_FILES_CACHE = getattr(settings,"DATABASE_FILES_CACHE", False)
DATABASE_FILES_CACHE_UNENCRYPTED = getattr(settings,"DATABASE_FILES_CACHE_UNENCRYPTED", False)
DATABASE_FILES_COMPRESSION_EXCLUDE = getattr(settings,"DATABASE_FILES_COMPRESSION_EXCLUDE",("zip", "gz", "rar", "jpg", "jpeg", "gif", "png", "mpg", "mpeg", "qt", "avi", "mov", "mkv"))
DATABASE_FILES_SECRET_KEY = getattr(settings,"DATABASE_FILES_SECRET_KEY", getattr(settings,"SECRET_KEY",None))

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
		string = file.read()
		self.size = file.size
		self.filepath = file.name

		if DATABASE_FILES_CACHE and DATABASE_FILES_CACHE_UNENCRYPTED:
			# Pre-fill the cache, the reasoning being that the file will probably be needed
			# immediately after storing
			cache.set(self.get_cache_key(), base64.binascii.b2a_hex(string))

		if compress:
			# Compress using zlib, this should be done before encryption
			if not self.get_extension() in DATABASE_FILES_COMPRESSION_EXCLUDE:
				string = zlib.compress(string)
				self.compressed = True

		if encrypt and cipher and DATABASE_FILES_SECRET_KEY:
			string = self._encrypt_string(string)
			self.encrypted = True

		self._store_string(self._encode_string(string))

		if DATABASE_FILES_CACHE and not DATABASE_FILES_CACHE_UNENCRYPTED:
			# Pre-fill the cache,
			cache.set(self.get_cache_key(), string)

		self.save()

	def _store_string(self, string):
		if self.filestore:
			self.filestore.delete()
		self.filestore = DatabaseFileStore(content=string)

	def _retreive_string(self):
		if self.filestore:
			return self.filestore.content
		else:
			return ""

	def retreive(self, mode="rb"):
		"""
		Constructs and returns a django file object from content
		"""

		if DATABASE_FILES_CACHE:
			string = cache.get(self.get_cache_key())
			if not string:
				string = self._decode_string(self._retreive_string())
				if not DATABASE_FILES_CACHE_UNENCRYPTED:
					string = self._process_string(string)
				cache.set(self.get_cache_key(), string)
			else:
				string = self._decode_string(self._retreive_string())
				string = self._process_string(string)
		else:
			string = self._decode_string(self._retreive_string())
			string = self._process_string(string)

		string_file = StringIO(string)
		django_file = files.File(string_file)
		django_file.name = self.filepath
		django_file.mode = mode
		django_file.size = self.size
		django_file.url = self.get_absolute_url()

		self.accessed_time = datetime.now()
		self.save()
		import pdb; pdb.debug()
		return django_file

	def _decode_string(self, string):
		return base64.b64decode(string)

	def _encode_string(self, string):
		return base64.b64encode((string))

	def _encrypt_string(self, string):
		# Encrypt using the AES algorithm and the site's Secret Key
		padding  = cipher.block_size - len(string) % cipher.block_size
		if padding and padding < cipher.block_size:
			string += "\0" + ''.join([random.choice(string.printable) for index in range(padding-1)])
		return cipher.encrypt(string)

	def _decrypt_string(self, string):
		if not cipher:
			raise DatabaseFilesEncryptionError("Trying to decrypt file '%s', encryption module not found" % self.filepath)
		if not DATABASE_FILES_SECRET_KEY:
			raise DatabaseFilesEncryptionError("Trying to decrypt file '%s', SECRET_KEY not set" % self.filepath)
		return cipher.decrypt().split('\0')[0]		

	def _process_string(self, string):
		if self.encrypted:
			string = self._decrypt_string(string)
		if self.compressed:
			string = zlib.decompress(string)
		return string

	def get_filename(self):
		dir_name, file_name = os.path.split(self.filepath)
		return file_name

	def get_path(self):
		dir_name, file_name = os.path.split(self.filepath)
		return dir_name

	def get_extension(self):
		filename = self.get_filename()
		file_root, file_ext = os.path.splitext(file_name)
		return file_ext

	def get_fileroot(self):
		filename = self.get_filename()
		file_root, file_ext = os.path.splitext(file_name)
		return file_root

	def get_cache_key(self):
		return "DJANGO-DATABASE_FILE-%s" % self.pk

