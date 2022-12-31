# -*- coding: utf-8 -*-
import shutil
import sys
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Article, Category
from django_sample_generator import constants
from django_sample_generator.__main__ import main
from django_sample_generator.fields import FieldGenerator


class TestCommand(TestCase):
	def tearDown(self):
		shutil.rmtree(settings.MEDIA_ROOT)

	def test_run_command(self):
		with patch('sys.stdout', new_callable=StringIO):
			call_command('create_sample_data', verbosity=3)
		call_command('create_sample_data')


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
		self.assertTrue(cm.getvalue()[0].isupper())

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
