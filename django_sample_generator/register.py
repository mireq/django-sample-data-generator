# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class GeneratorRegister(object):
	def __init__(self):
		self.generators = []
		self.bulk_size = 1000

	def register(self, obj):
		self.generators.append(obj)

	def generate(self, command=None):
		bulk = []
		for generator in self.generators:
			generator.command = command
			if command is not None and command.verbosity > 1:
				command.stdout.write('\nGenerating ' + generator.__class__.__name__ + ' ', ending='')
				command.stdout.flush()
			for obj in generator:
				if command is not None and command.verbosity > 1:
					command.stdout.write('.', ending='')
					command.stdout.flush()
				bulk.append(obj)
				if len(bulk) >= self.bulk_size:
					bulk[0].__class__.objects.bulk_create(bulk)
					bulk = []
			if bulk:
				bulk[0].__class__.objects.bulk_create(bulk)
				bulk = []
			generator.done()
