# -*- coding: utf-8 -*-
# pylint: disable=no-member
from django.utils import six


class MetaOpts:
	model = None
	fill_optional = False


class ModelGeneratorBase(type):
	def __new__(cls, name, bases, attrs):
		new_class = super(ModelGeneratorBase, cls).__new__(cls, name, bases, attrs)
		opts = getattr(new_class, 'Meta', MetaOpts)
		opts.model = getattr(opts, 'model', MetaOpts.model)
		opts.fill_optional = getattr(opts, 'fill_optional', MetaOpts.fill_optional)
		new_class._meta = opts
		return new_class


class ModelGenerator(six.with_metaclass(ModelGeneratorBase)):
	command = None

	def __init__(self, count=0, model=None):
		self.model = model
		self.count = count
		if self.model is None:
			self.model = self._meta.model


#class ModelGenerator(object):
#	command = None
#
#	def __init__(self, model, count=0):
#		self.model = model
#		self.count = count
#
#	def __iter__(self):
#		for __ in range(self.get_count()):
#			yield self.get_object()
#
#	def get_count(self):
#		return self.count
#
#	def get_object(self):
#		obj = self.model()
#		members = inspect.getmembers(self, lambda o: isinstance(o, Sample))
#		for name, member in members:
#			setattr(obj, name, member.get_sample())
#		return obj
#
#	def done(self):
#		pass
