# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.module_loading import import_string

from ...register import GeneratorRegister


class Command(BaseCommand):
	verbosity = 0

	def handle(self, *args, **options):
		self.verbosity = options.get('verbosity')

		register = GeneratorRegister()
		generators = getattr(settings, 'SAMPLE_DATA_GENERATORS', ())
		for generator_path in generators:
			generator_module = import_string(generator_path + '.generators')
			for generator in generator_module:
				register.register(generator)
		with transaction.atomic():
			register.generate(command=self)
