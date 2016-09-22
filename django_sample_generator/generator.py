# -*- coding: utf-8 -*-
import inspect

from .samples import Sample


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


class ModelGenerator(object):
	command = None

	def __init__(self, model, count=0):
		self.model = model
		self.count = count

	def __iter__(self):
		for __ in range(self.get_count()):
			yield self.get_object()

	def get_count(self):
		return self.count

	def get_object(self):
		obj = self.model()
		members = inspect.getmembers(self, lambda o: isinstance(o, Sample))
		for name, member in members:
			setattr(obj, name, member.get_sample())
		return obj

	def next(self):
		if self.num < self.get_count():
			obj = self.get_object()
			self.num += 1
			return obj
		else:
			raise StopIteration()

	def done(self):
		pass
