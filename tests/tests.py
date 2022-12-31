# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.test import TestCase


class TestCommand(TestCase):
	def test_run_command(self):
		call_command('create_sample_data', verbosity=3)
		call_command('create_sample_data')
