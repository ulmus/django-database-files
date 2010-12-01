django-database-files
=====================

django-database-files is a storage system for Django that stores uploaded files 
in the database.

BIG SCARY WARNING: It is generally a bad idea to serve static files from Django, 
but there are some valid use cases. If your Django app is behind a caching 
reverse proxy and you need to scale your application servers, it may be 
simpler to store files in the database instead of using a distributed 
filesystem.

Requires:

  * Django 1.1
  * For encryption, PyCrypt

 Supports the new file storage methods in Django 1.3

Installation
------------

    $ python setup.py install

Usage
-----

In ``settings.py``, add ``database_files`` to your ``INSTALLED_APPS`` and add this line:

    DEFAULT_FILE_STORAGE = 'database_files.storage.DatabaseStorage'

The ``upload_to`` argument is used to construct a unique identifier for the file and
django-database-files will act as a normal filesystem when seen from Django, including
renaming of identical files.

All your ``FileField`` and ``ImageField`` files will now be stored in the 
database.

Compression
-----------

If ``DATABASE_FILES_COMPRESSION`` or the DatabaseStorage optional parameter compression is set to True, the
files are compressed using zlib. To avoid compressing certain file types, you can provide a
``DATABASE_FILES_COMPRESSION_EXCLUDE`` setting with a list of file types not to compress. The default settings are
	
	DATABASE_FILES_COMPRESSION = False
	DATABASE_FILES_COMPRESSION_EXCLUDE = ("zip", "gz", "rar", "jpg", "jpeg", "gif", "png", "mpg", "mpeg", "qt", "avi", "mov", "mkv")

Encryption
----------

If  ``DATABASE_FILES_ENCRYPTION`` or the DatabaseStorage optional parameter encryption is set to True, the
files are encrypted using AES and your ``DATABASE_FILES_SECRET_KEY`` that defaults to your ´´SECRET_KEY´´.

	DATABASE_FILES_ENCRYPTION = False
	DATABASE_FILES_SECRET_KEY = SECRET_KEY


Caching
-------

If ``DATABASE_FILES_CACHE`` is set, the DatabaseStorage will use the cache provided in the ``CACHE_BACKEND`` to cache file
content to avoid hitting the database on each file request. Files will still be served through django which is inherently much slower
than using your webserver so you still shouldn't serve static files this way. Also note that the files are cached
encrypted and zipped if those options are used. If this is not the desired behaviour, set ``DATABASE_FILES_CACHE_UNENCRYPTED`` to True to gain some
performance.

	DATABASE_FILES_CACHE = False
	DATABASE_FILES_CACHE_UNENCRYPTED = False


Troubleshooting
---------------

If you get the error message ``OperationalError: (1153, "Got a packet bigger than 'max_allowed_packet' bytes")`` this means that the file is
larger than what your mysql server accepts (usually 1 MB). This can be resolved by setting the ``max_allowed_packet`` setting in your ``my.cnf`` file
to a higher number and by sanitizing your file upload handling to discard files larger than that size. Database storage is probably not meant for huge
media files!