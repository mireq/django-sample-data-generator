# -*- coding: utf-8 -*-
import shutil
import sys
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings

from .generators_functions import set_test as set_function_test
from .generators_unique_fail import set_test as set_unique_test
from .models import Article, Category, Foo, UniqueTogether
from django_sample_generator import constants
from django_sample_generator.__main__ import main
from django_sample_generator.fields import FieldGenerator
from django_sample_generator.functions import trim_text
from django_sample_generator.text_generator import get_text_generator


class TestCommand(TestCase):
	def tearDown(self):
		shutil.rmtree(settings.MEDIA_ROOT)

	def test_run_command(self):
		call_command('create_sample_data')
		with override_settings(USE_TZ=True):
			with patch('sys.stdout', new_callable=StringIO):
				call_command('create_sample_data', verbosity=3)


class TestCommandline(TestCase):
	def test_no_argument(self):
		with patch('sys.stdout', new_callable=StringIO):
			with self.assertRaises(SystemExit) as cm:
				main()
		self.assertEqual(-1, cm.exception.code)

	def test_too_many_argument(self):
		with patch.object(sys, 'argv', ['main', 'w', '1', '2']):
			with patch('sys.stdout', new_callable=StringIO):
				with self.assertRaises(SystemExit) as cm:
					main()
		self.assertEqual(-1, cm.exception.code)

	def test_wrong_argument(self):
		with patch.object(sys, 'argv', ['main', '?']):
			with patch('sys.stdout', new_callable=StringIO):
				with self.assertRaises(SystemExit) as cm:
					main()
		self.assertEqual(-1, cm.exception.code)

	def test_wrong_number(self):
		with patch.object(sys, 'argv', ['main', 'w', 'x']):
			with patch('sys.stdout', new_callable=StringIO):
				with self.assertRaises(SystemExit) as cm:
					main()
		self.assertEqual(-1, cm.exception.code)

	def test_word(self):
		with patch.object(sys, 'argv', ['main', 'w']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()
		self.assertNotEqual('', cm.getvalue())

		# minimum length
		with patch.object(sys, 'argv', ['main', 'w', '10']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()
		self.assertGreaterEqual(len(cm.getvalue()), 10)

		with patch.object(sys, 'argv', ['main', 'uw']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()
		self.assertNotEqual('', cm.getvalue())
		self.assertTrue(cm.getvalue()[0].istitle())

	def test_sentence(self):
		with patch.object(sys, 'argv', ['main', 's']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()
		self.assertIn(cm.getvalue()[-1], constants.SENTENCE_END)

	def test_paragraph(self):
		with patch.object(sys, 'argv', ['main', 'p']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()
		self.assertIn(cm.getvalue()[-1], constants.SENTENCE_END)

		# exact length
		with patch.object(sys, 'argv', ['main', 'p', '2']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()

		text = cm.getvalue()
		sentence_ends = 0
		for c in constants.SENTENCE_END:
			sentence_ends += text.count(c)

		self.assertEqual(2, sentence_ends)

	def test_text(self):
		with patch.object(sys, 'argv', ['main', 't']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()
		self.assertIn(cm.getvalue()[-1], constants.SENTENCE_END)

		# exact length
		with patch.object(sys, 'argv', ['main', 't', '2']):
			with patch('sys.stdout', new_callable=StringIO) as cm:
				main()

		self.assertEqual(1, cm.getvalue().count('\n'))


@override_settings(SAMPLE_DATA_GENERATORS=['tests.generators_manually_defined'])
class TestGenerator(TestCase):
	def test_not_implemented(self):
		with self.assertRaises(NotImplementedError):
			next(iter(FieldGenerator()))

	def test_manually_defined(self):
		call_command('create_sample_data')
		self.assertEqual(
			list(Article.objects.order_by('pk').values_list('category_id', flat=True)),
			list(Category.objects.order_by('pk').values_list('pk', flat=True)),
		)


class TestTextGenerator(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.gen = get_text_generator()

	def test_long_word(self):
		self.assertGreaterEqual(len(self.gen.get_word(min_length=30)), 30)


@override_settings(SAMPLE_DATA_GENERATORS=['tests.generators_functions'])
class TestFunctions(TestCase):
	def get_field_values(self):
		return list(Foo.objects.values_list('field', flat=True))

	def test_trim(self):
		# don't throw exception on None
		self.assertIsNone(trim_text(None))

	def test_blank(self):
		set_function_test('blank')
		call_command('create_sample_data')
		self.assertEqual([''], self.get_field_values())

	def test_blank_slug(self):
		set_function_test('blank_slug')
		call_command('create_sample_data')
		self.assertEqual([''], self.get_field_values())

	def test_seq(self):
		set_function_test('seq')
		call_command('create_sample_data')
		self.assertEqual(['10', '15'], self.get_field_values())

	def test_seq_choice(self):
		set_function_test('seq_choice')
		call_command('create_sample_data')
		self.assertEqual(['A', 'B'], self.get_field_values())

	def test_text(self):
		set_function_test('text')
		call_command('create_sample_data')
		# trimmed to 1 character
		self.assertEqual(1, len(self.get_field_values()[0]))

	def test_bulk(self):
		set_function_test('bulk')
		call_command('create_sample_data')
		# without overflow
		self.assertEqual(['1', '2'], self.get_field_values())

	def test_bulk2(self):
		set_function_test('bulk2')
		call_command('create_sample_data')
		# with overflow
		self.assertEqual(['1', '2', '3'], self.get_field_values())


class TestModelGenerator(TestCase):
	@override_settings(SAMPLE_DATA_GENERATORS=['tests.generators_not_registered'])
	def test_wrong_field(self):
		set_unique_test('unique_together')
		with self.assertRaises(RuntimeError):
			call_command('create_sample_data')

	@override_settings(SAMPLE_DATA_GENERATORS=['tests.generators_unique_fail'])
	def test_unique_failed(self):
		set_unique_test('unique_together')
		call_command('create_sample_data')
		with self.assertRaises(RuntimeError):
			call_command('create_sample_data')

	@override_settings(SAMPLE_DATA_GENERATORS=['tests.generators_unique_fail'])
	def test_partial(self):
		set_unique_test('unique_partial')
		call_command('create_sample_data')
		self.assertEqual([(0, 0), (1, 1)], list(UniqueTogether.objects.order_by('pk').values_list('foo', 'bar')))
