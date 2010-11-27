from django.db import models
from database_files.storage import DatabaseStorage

class Thing(models.Model):
    upload = models.FileField(upload_to='things/', storage=DatabaseStorage())

class EncryptedThing(models.Model):
    upload = models.FileField(upload_to='things/', storage=DatabaseStorage(encrypt=True))

class CompressedThing(models.Model):
	upload = models.FileField(upload_to='things/', storage=DatabaseStorage(compress=True))

class CompressedEncryptedThing(models.Model):
	upload = models.FileField(upload_to='things/', storage=DatabaseStorage(compress=True, encrypt=True))
