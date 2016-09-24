# -*- coding: utf-8 -*-
# pylint: disable=no-member
import inspect
from copy import copy

from collections import defaultdict
from django.conf import settings
from django.db import models
from django.utils import six

from .fields import GENERATOR_FOR_DBFIELD, FieldGenerator


GENERATORS = copy(GENERATOR_FOR_DBFIELD)
GENERATORS.update(getattr(settings, 'GENERATOR_FOR_DBFIELD', {}))


class MetaOpts:
	model = None
	fill_optional = False
	unique_checks = []
	field_kwargs = {}
	fields = None
	exclude = ()


def field_to_generator(field, opts):
	fill_optional = opts.fill_optional
	if field.blank == True and (fill_optional == False or (fill_optional != True and field.name not in fill_optional)):
		return {} # skip optional
	if opts.fields is not None and field.name not in opts.fields:
		return {}
	if field.name in opts.exclude:
		return {}
	field_cls = field.__class__
	if field_cls in GENERATORS:
		return {field.name: GENERATORS[field_cls](field, **opts.field_kwargs.get(field.name, {}))}
	else:
		raise RuntimeError("Field %s is not registered" % str(field_cls))


class ModelGeneratorBase(type):
	def __new__(cls, name, bases, attrs):
		new_class = super(ModelGeneratorBase, cls).__new__(cls, name, bases, attrs)
		opts = getattr(new_class, 'Meta', MetaOpts)
		opts.model = getattr(opts, 'model', MetaOpts.model)
		opts.fill_optional = getattr(opts, 'fill_optional', MetaOpts.fill_optional)
		opts.unique_checks = getattr(opts, 'unique_checks', MetaOpts.unique_checks)
		opts.field_kwargs = getattr(opts, 'field_kwargs', MetaOpts.field_kwargs)
		opts.fields = getattr(opts, 'fields', MetaOpts.fields)
		opts.exclude = getattr(opts, 'exclude', MetaOpts.exclude)
		new_class._meta = opts
		new_class.generators = {}

		if opts.model:
			for field in opts.model._meta.fields:
				if isinstance(field, models.AutoField):
					continue
				if field.unique:
					opts.unique_checks.append((field.name,))
				if hasattr(new_class, field.name):
					continue
				gen = field_to_generator(field, opts)
				if not gen:
					continue
				for key, field_generator in gen.items():
					setattr(new_class, key, field_generator)
			for check in opts.model._meta.unique_together:
				opts.unique_checks.append(tuple(check))

		generators = inspect.getmembers(new_class, lambda o: isinstance(o, FieldGenerator))
		for name, generator in generators:
			new_class.generators[name] = iter(generator)
		return new_class


class ModelGenerator(six.with_metaclass(ModelGeneratorBase)):
	command = None
	unique_values = None

	def __init__(self, count=0, model=None):
		self.model = model
		self.count = count
		self.unique_values = defaultdict(set)
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
			try:
				setattr(obj, name, next(generator))
			except StopIteration:
				print("Stop iteration on %s" % name)
				raise
		errors = set()
		for __ in range(100):
			errors = self.get_unique_errors(obj)
			if not errors:
				break
			for name, generator in self.generators.items():
				if name in errors:
					setattr(obj, name, next(generator))
		if errors:
			raise RuntimeError("Unique check failed for fields %s" % ", ".join(errors))
		else:
			self.write_unique(obj)
		return obj

	def get_unique_errors(self, obj):
		unique_errors = set()
		for check in self._meta.unique_checks:
			val = tuple(getattr(obj, field) for field in check)
			if val in self.unique_values[check]:
				unique_errors.update(check)
		return unique_errors

	def write_unique(self, obj):
		for check in self._meta.unique_checks:
			val = tuple(getattr(obj, field) for field in check)
			self.unique_values[check].add(val)

	def done(self):
		pass
