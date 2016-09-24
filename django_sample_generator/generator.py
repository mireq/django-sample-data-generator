# -*- coding: utf-8 -*-
# pylint: disable=no-member
import inspect
from copy import copy

from django.conf import settings
from django.db import models
from django.utils import six

from .fields import GENERATOR_FOR_DBFIELD, FieldGenerator


GENERATORS = copy(GENERATOR_FOR_DBFIELD)
GENERATORS.update(getattr(settings, 'GENERATOR_FOR_DBFIELD', {}))


class MetaOpts:
	model = None
	fill_optional = False


def field_to_generator(field, opts):
	if isinstance(field, models.AutoField):
		return {}
	fill_optional = opts.fill_optional
	if field.blank == True and (fill_optional == False or (fill_optional != True and field.name not in fill_optional)):
		return {} # skip optional
	field_cls = field.__class__
	if field_cls in GENERATORS:
		return {field.name: GENERATORS[field_cls](field)}
	return {}


class ModelGeneratorBase(type):
	def __new__(cls, name, bases, attrs):
		new_class = super(ModelGeneratorBase, cls).__new__(cls, name, bases, attrs)
		opts = getattr(new_class, 'Meta', MetaOpts)
		opts.model = getattr(opts, 'model', MetaOpts.model)
		opts.fill_optional = getattr(opts, 'fill_optional', MetaOpts.fill_optional)
		new_class._meta = opts
		new_class.generators = {}

		if opts.model:
			for field in opts.model._meta.fields:
				if hasattr(new_class, field.name):
					continue
				gen = field_to_generator(field, opts)
				if not gen:
					continue
				for key, field_generator in gen.items():
					setattr(new_class, key, field_generator)

		generators = inspect.getmembers(new_class, lambda o: isinstance(o, FieldGenerator))
		for name, generator in generators:
			new_class.generators[name] = iter(generator)
		return new_class


class ModelGenerator(six.with_metaclass(ModelGeneratorBase)):
	command = None

	def __init__(self, count=0, model=None):
		self.model = model
		self.count = count
		if self.model is None:
			self.model = self._meta.model

	def __iter__(self):
		for __ in range(self.get_count()):
			yield self.get_object()

	def get_count(self):
		return self.count

	def get_object(self):
		obj = self.model()
		for name, generator in self.generators.items():
			setattr(obj, name, next(generator))
		return obj

	def done(self):
		pass
