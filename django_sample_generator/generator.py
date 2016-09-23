# -*- coding: utf-8 -*-
import inspect

from .samples import Sample


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

	def done(self):
		pass
