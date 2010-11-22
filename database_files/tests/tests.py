# -*- coding: utf-8 -*-
from database_files.models import DatabaseFile
from database_files.module_settings import DBF_SETTINGS
from database_files.tests.models import Thing
from django.core.cache import cache
from django.core import files
from django.test import TestCase
import StringIO

def create_test_object(estring):
	test_file = files.temp.NamedTemporaryFile(
			suffix='.txt',
			dir=files.temp.gettempdir()
			)
	test_file.write(estring)
	test_file.seek(0)
	t = Thing.objects.create(
			upload=files.File(test_file),
			)
	return t, test_file

class DatabaseFilesTestCase(TestCase):

	def test_adding_file(self):
		t, test_file = create_test_object('1234567890')
		self.assertEqual(DatabaseFile.objects.count(), 1)
		t = Thing.objects.get(pk=t.pk)
		self.assertEqual(t.upload.file.size, 10)
		self.assertEqual(t.upload.file.name, test_file.name)
		self.assertEqual(t.upload.file.read(), '1234567890')
		t.upload.delete()
		self.assertEqual(DatabaseFile.objects.count(), 0)

class DatabaseFilesViewTestCase(TestCase):

	def test_create_and_readback_file(self):
		t, test_file = create_test_object('1234567890')
		response = self.client.get('/1')
		self.assertEqual(response.content, '1234567890')
		self.assertEqual(response['content-type'], 'text/plain')
		self.assertEqual(unicode(response['content-length']), '10')

	def test_content_in_database(self):
		estring = '1234567890'
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		response = self.client.get('/1')
		self.assertFalse(database_file.encrypted)
		self.assertFalse(database_file.compressed)
		self.assertEqual(response.content, estring)
		self.assertEqual(database_file.get_decoded_string(), estring)
		self.assertNotEqual(database_file.get_raw_string(), estring)

	def test_international_characters(self):
		estring = u"äåöü£[|§±≈]ﬁª√ıüµ][ıü˛√›‹√˛ƒµ†®†®ß"
		t, test_file = create_test_object(estring)
		response = self.client.get('/1')
		self.assertEqual(response.content, estring)

class DatabaseFilesEncryptedTestCase(DatabaseFilesViewTestCase):

	def setUp(self):
		self.encryption_setting = DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"]
		DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"] = True
		super(DatabaseFilesEncryptedTestCase, self).setUp()

	def test_content_in_database(self):
		estring = '1234567890'
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"])
		self.assertTrue(database_file.encrypted)
		response = self.client.get('/1')
		self.assertEqual(response.content, estring)
		self.assertNotEqual(database_file.get_decoded_string(), estring)
		self.assertNotEqual(database_file.get_raw_string(), estring)

	def tearDown(self):
		DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"] = self.encryption_setting
		super(DatabaseFilesEncryptedTestCase, self).tearDown()


class DatabaseFilesCompressedTestCase(DatabaseFilesViewTestCase):

	def setUp(self):
		self.compression_setting = DBF_SETTINGS["DATABASE_FILES_COMPRESSION"]
		DBF_SETTINGS["DATABASE_FILES_COMPRESSION"] = True
		super(DatabaseFilesCompressedTestCase, self).setUp()

	def test_content_in_database(self):
		estring = '1234567890'
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_COMPRESSION"])
		self.assertTrue(database_file.compressed)
		response = self.client.get('/1')
		self.assertEqual(response.content, estring)
		self.assertNotEqual(database_file.get_decoded_string(), estring)
		self.assertNotEqual(database_file.get_raw_string(), estring)

	def test_compression_level(self):
		estring = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In a pulvinar felis. Nunc in libero in tellus rutrum ultrices. Quisque a tellus ut nunc elementum pulvinar. Aenean ligula turpis, vestibulum a pretium vel, euismod eu leo. Suspendisse vitae scelerisque eros. Cras purus nisl, hendrerit eget sodales eu, aliquam at ligula. Integer purus enim, aliquet at feugiat vitae, feugiat non est. Pellentesque lorem massa, convallis in congue et, tincidunt et nulla. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Nunc blandit pulvinar vehicula. Morbi placerat massa ut lorem imperdiet a pulvinar augue bibendum. Donec id condimentum erat. Pellentesque eu nunc urna. Phasellus vel pharetra nisl. Phasellus convallis pulvinar dolor, vel hendrerit diam iaculis non.
Praesent posuere nisl in tortor varius vitae ullamcorper tellus elementum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc lobortis sapien molestie lectus accumsan sed fermentum metus bibendum. Aliquam erat volutpat. Vivamus consectetur eleifend dictum. Curabitur ac purus augue, et semper dui. Nunc adipiscing sagittis nunc nec sagittis. Etiam turpis purus, iaculis a pretium eget, egestas non enim. Suspendisse et dui ac neque accumsan feugiat congue sit amet lorem. Mauris lobortis tempor dolor nec congue. Nam elementum neque quam.
Vivamus sit amet metus ullamcorper lectus sollicitudin faucibus. Nunc ullamcorper ligula vel neque adipiscing consequat. Suspendisse potenti. Nullam eu lacus at nunc hendrerit ullamcorper et a augue. Integer quis purus turpis. Donec iaculis mauris sit amet mauris feugiat quis interdum tellus sollicitudin. Nulla facilisi. Quisque a velit nulla, ut sodales eros. Proin euismod tortor rutrum massa bibendum quis cursus arcu porttitor. Suspendisse venenatis, risus quis hendrerit accumsan, libero arcu malesuada est, eget porta ipsum mauris eu purus. Donec sollicitudin pharetra diam. Ut id laoreet turpis. Fusce ut urna massa. Donec laoreet bibendum dui, sed hendrerit odio commodo condimentum. Curabitur sagittis semper nibh. Praesent fringilla turpis et nibh molestie rhoncus. Maecenas vehicula lorem rutrum neque malesuada facilisis. Proin molestie, elit a ultricies dapibus, orci ante auctor nisi, vitae tincidunt diam ante eu massa. Nulla varius, tortor vel varius imperdiet, dolor nunc ornare justo, et consequat dui enim vitae lacus. Integer aliquam leo ut sapien imperdiet viverra.
Praesent pretium dignissim ultricies. Praesent volutpat tincidunt dui, pharetra fermentum diam pulvinar at. Quisque egestas sem at lectus mollis in molestie ante tempor. Aenean adipiscing ipsum non elit interdum sit amet varius sapien iaculis. Phasellus pretium enim venenatis lorem blandit a vulputate nibh dictum. Etiam non nibh nec mi gravida suscipit sit amet in eros. Sed non lacus vitae nunc sodales malesuada et quis libero. Cras dignissim mi et dui pulvinar iaculis. Sed vel ligula bibendum felis euismod luctus in sit amet sem. Ut eget magna metus. Etiam consectetur turpis nibh. Nunc ac vestibulum quam. Proin vel dolor felis. Phasellus nisi urna, imperdiet id molestie eget, rhoncus a diam. Praesent aliquam consequat leo a imperdiet. Sed quis urna ipsum. Nulla vel metus tellus, at tincidunt odio.
Pellentesque metus ligula, commodo quis lacinia id, aliquam nec libero. Morbi nulla eros, lobortis ac faucibus fermentum, aliquam vitae massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Fusce aliquam lacinia aliquet. Aenean at tincidunt tellus. Donec sagittis eleifend erat non viverra. Nulla facilisi. Aliquam sit amet pretium diam. Cras vitae felis nec est pretium vulputate. Praesent odio tellus, facilisis et viverra a, mollis aliquet risus.
		"""
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		db_length = len(database_file.get_raw_string())
		estring_length = len(estring)
		print "Compression saved " + unicode((estring_length - db_length) * 100 / estring_length) + "%"
		self.assertTrue(db_length < estring_length)

	def tearDown(self):
		DBF_SETTINGS["DATABASE_FILES_COMPRESSION"] = self.compression_setting
		super(DatabaseFilesCompressedTestCase, self).tearDown()

class DatabaseFilesCompressedEncryptedTestCase(DatabaseFilesCompressedTestCase):

	def setUp(self):
		self.encryption_setting = DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"]
		DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"] = True
		super(DatabaseFilesCompressedEncryptedTestCase, self).setUp()

	def test_encrypted_vs_unencrypted(self):
		estring = '1234567890'
		t_enc, test_file_enc = create_test_object(estring)
		database_file_enc = DatabaseFile.objects.get(pk=1)
		response_enc = self.client.get('/1')
		DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"] = False
		t_nenc, test_file_nenc = create_test_object(estring)
		database_file_nenc = DatabaseFile.objects.get(pk=2)
		response_nenc = self.client.get('/2')
		DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"] = False
		self.assertTrue(database_file_enc.encrypted)
		self.assertFalse(database_file_nenc.encrypted)
		self.assertFalse(database_file_enc.get_raw_string() == database_file_nenc.get_raw_string())
		self.assertTrue(response_enc.content == response_nenc.content)

	def test_content_in_database(self):
		estring = '1234567890'
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_COMPRESSION"])
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"])
		self.assertTrue(database_file.compressed)
		self.assertTrue(database_file.encrypted)
		response = self.client.get('/1')
		self.assertEqual(response.content, estring)
		self.assertNotEqual(database_file.get_decoded_string(), estring)
		self.assertNotEqual(database_file.get_raw_string(), estring)

	def tearDown(self):
		DBF_SETTINGS["DATABASE_FILES_ENCRYPTION"] = self.encryption_setting
		super(DatabaseFilesCompressedEncryptedTestCase, self).tearDown()

class DatabaseFilesCacheTestCase(DatabaseFilesViewTestCase):

	def setUp(self):
		self.cache_setting = DBF_SETTINGS["DATABASE_FILES_CACHE"]
		DBF_SETTINGS["DATABASE_FILES_CACHE"] = True
		super(DatabaseFilesCacheTestCase, self).setUp()

	def test_caching(self):
		estring = '1234567890'
		fstring = 'abcdefghij'
		cache_key1 = "DJANGO-DATABASE_FILE-1"
		cache_key2 = "DJANGO-DATABASE_FILE-2"
		cache.set(cache_key1, None)
		self.assertFalse(cache.get(cache_key1))
		cache.set(cache_key2, None)
		self.assertFalse(cache.get(cache_key2))
		t1, test_file1 = create_test_object(estring)
		t2, test_file2 = create_test_object(fstring)
		database_file1 = DatabaseFile.objects.get(pk=1)
		database_file2 = DatabaseFile.objects.get(pk=2)
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_CACHE"])
		self.assertTrue(cache.get(cache_key1))
		response1 = self.client.get('/1')
		response2 = self.client.get('/2')
		self.assertEqual(database_file1.get_raw_string(), cache.get(cache_key1))
		self.assertEqual(database_file2.get_raw_string(), cache.get(cache_key2))




	def tearDown(self):
		DBF_SETTINGS["DATABASE_FILES_CACHE"] = self.cache_setting
		super(DatabaseFilesCacheTestCase, self).tearDown()

class DatabaseFilesCompressedEncryptedCachedTestCase(DatabaseFilesCompressedEncryptedTestCase):

	def setUp(self):
		self.cache_setting = DBF_SETTINGS["DATABASE_FILES_CACHE"]
		DBF_SETTINGS["DATABASE_FILES_CACHE"] = True
		super(DatabaseFilesCompressedEncryptedCachedTestCase, self).setUp()

	def test_caching(self):
		estring = '1234567890'
		cache_key = "DJANGO-DATABASE_FILE-1"
		cache.set(cache_key, None)
		self.assertFalse(cache.get(cache_key))
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_CACHE"])
		response = self.client.get('/1')
		self.assertTrue(cache.get(cache_key))
		# Check that the cache is encrypted:
		self.assertNotEqual(response.content, cache.get(cache_key))

	def tearDown(self):
		DBF_SETTINGS["DATABASE_FILES_CACHE"] = self.cache_setting
		super(DatabaseFilesCompressedEncryptedCachedTestCase, self).tearDown()

class DatabaseFilesCompressedEncryptedCachedUnencryptedTestCase(DatabaseFilesCompressedEncryptedCachedTestCase):

	def setUp(self):
		self.cache_unencrypted_setting = DBF_SETTINGS["DATABASE_FILES_CACHE_UNENCRYPTED"]
		DBF_SETTINGS["DATABASE_FILES_CACHE_UNENCRYPTED"] = True
		super(DatabaseFilesCompressedEncryptedCachedUnencryptedTestCase, self).setUp()

	def test_caching(self):
		cache_key = "DJANGO-DATABASE_FILE-1"
		estring = '1234567890'
		cache.set(cache_key, None)
		t, test_file = create_test_object(estring)
		database_file = DatabaseFile.objects.get(pk=1)
		self.assertTrue(DBF_SETTINGS["DATABASE_FILES_CACHE"])
		response = self.client.get('/1')
		# Check that the cache is not encrypted:
		self.assertEqual(response.content, cache.get(cache_key))

	def tearDown(self):
		DBF_SETTINGS["DATABASE_FILES_CACHE_UNENCRYPTED"] = self.cache_unencrypted_setting
		super(DatabaseFilesCompressedEncryptedCachedUnencryptedTestCase, self).tearDown()
