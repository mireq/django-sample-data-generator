# -*- coding: utf-8 -*-
import os

import urllib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string


class Command(BaseCommand):
	verbosity = 0

	def handle(self, *args, **options):
		self.verbosity = options.get('verbosity')

		generators = getattr(settings, 'SAMPLE_DATA_GENERATORS', ())
		for generator in generators:
			generator_object = import_string(generator)
			generator_object.generate(command=self)
