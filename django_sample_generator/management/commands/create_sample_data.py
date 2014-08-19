# -*- coding: utf-8 -*-
import os

import urllib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_by_path


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		generators = getattr(settings, 'SAMPLE_DATA_GENERATORS', ())
		for generator in generators:
			generator_object = import_by_path(generator)
			generator_object.generate()
