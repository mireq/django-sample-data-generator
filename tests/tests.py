# -*- coding: utf-8 -*-
import shutil

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class TestCommand(TestCase):
	def tearDown(self):
		shutil.rmtree(settings.MEDIA_ROOT)

	def test_run_command(self):
		call_command('create_sample_data', verbosity=3)
		call_command('create_sample_data')
