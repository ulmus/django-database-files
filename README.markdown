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

Although ``upload_to`` is a required argument on ``FileField``, it is not used for 
storing files in the database. Just set it to a dummy value:

    upload = models.FileField(upload_to='not required')

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

If ``DATABASE_FILES_CACHE`` is set, the DatabaseStorage will use the cache provided in the ´´´CACHE_BACKEND´´ to cache file
content to avoid hitting the database on each file request. Files will still be served through django which is inherently much slower
than using your webserver so you still shouldn't serve static files this way. Also note that the files are cached
encrypted and zipped if thos options are used.

	DATABASE_FILES_CACHE = False
