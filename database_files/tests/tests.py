from django.core import files
from django.test import TestCase
from database_files.models import DatabaseFile
from database_files.tests.models import Thing
import StringIO

def create_test_object():
	test_file = files.temp.NamedTemporaryFile(
			suffix='.txt',
			dir=files.temp.gettempdir()
			)
	test_file.write('1234567890')
	test_file.seek(0)
	t = Thing.objects.create(
			upload=files.File(test_file),
			)
	return t, test_file

class DatabaseFilesTestCase(TestCase):
	def test_adding_file(self):
		t, test_file = create_test_object()
		self.assertEqual(DatabaseFile.objects.count(), 1)
		t = Thing.objects.get(pk=t.pk)
		self.assertEqual(t.upload.file.size, 10)
		self.assertEqual(t.upload.file.name, test_file.name)
		self.assertEqual(t.upload.file.read(), '1234567890')
		t.upload.delete()
		self.assertEqual(DatabaseFile.objects.count(), 0)

class DatabaseFilesViewTestCase(TestCase):

	def test_create_and_readback_file(self):
		t, test_file = create_test_object()
		response = self.client.get('/1')
		self.assertEqual(response.content, '1234567890')
		self.assertEqual(response['content-type'], 'text/plain')
		self.assertEqual(unicode(response['content-length']), '10')

