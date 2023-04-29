# -*- coding: utf-8 -*-
# pylint: disable=no-member
import inspect
from copy import copy

from collections import defaultdict
from django.conf import settings
from django.db import models
from django.core.exceptions import FieldDoesNotExist

from .fields import GENERATOR_FOR_DBFIELD, FieldGenerator


GENERATORS = copy(GENERATOR_FOR_DBFIELD)
GENERATORS.update(getattr(settings, 'GENERATOR_FOR_DBFIELD', {}))


class MetaOpts:
	model = None
	unique_checks = []
	field_kwargs = {}
	fields = None
	exclude = ()


def field_to_generator(field, opts):
	if opts.fields is not None and field.name not in opts.fields:
		return None
	if field.name in opts.exclude:
		return None
	field_cls = field.__class__
	if field_cls in GENERATORS:
		return GENERATORS[field_cls](**opts.field_kwargs.get(field.name, {}))
	else:
		raise RuntimeError("Field %s (%s) is not registered" % (field.name, str(field_cls)))


class ModelGeneratorBase(type):
	def __new__(cls, name, bases, attrs):
		new_class = super(ModelGeneratorBase, cls).__new__(cls, name, bases, attrs)
		opts = getattr(new_class, 'Meta', None)
		if opts is None:
			opts = type('Meta', (MetaOpts,), {})
		opts.model = getattr(opts, 'model', MetaOpts.model)
		opts.unique_checks = list(getattr(opts, 'unique_checks', MetaOpts.unique_checks))
		opts.field_kwargs = copy(getattr(opts, 'field_kwargs', MetaOpts.field_kwargs))
		opts.fields = copy(getattr(opts, 'fields', MetaOpts.fields))
		opts.exclude = copy(getattr(opts, 'exclude', MetaOpts.exclude))
		new_class._meta = opts
		new_class._meta.generators = {}

		if opts.model:
			for field in opts.model._meta.fields:
				if isinstance(field, models.AutoField):
					continue
				gen = field_to_generator(field, opts)
				if gen is not None and field.unique:
					opts.unique_checks.append((field.name,))
				if hasattr(new_class, field.name) or not gen:
					continue
				setattr(new_class, field.name, gen)
			for check in opts.model._meta.unique_together:
				opts.unique_checks.append(tuple(check))

		generators = inspect.getmembers(new_class, lambda o: isinstance(o, FieldGenerator))
		for field_name, generator in generators:
			if opts.model is not None:
				try:
					generator.field = opts.model._meta.get_field(field_name)
				except FieldDoesNotExist:
					pass
			new_class._meta.generators[field_name] = iter(generator)
		return new_class


class ModelGenerator(object, metaclass=ModelGeneratorBase):
	unique_values = None
	bulk_size = 1000

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

	def build_instance(self):
		return self.model()

	def get_object(self):
		obj = self.build_instance()
		for name, generator in self._meta.generators.items():
			setattr(obj, name, next(generator))
		errors = set()
		for __ in range(100):
			errors = self.get_unique_errors(obj)
			if not errors:
				break
			for name, generator in self._meta.generators.items():
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
			skip_check = False
			for field in check:
				if field not in self._meta.generators:
					skip_check = True
			if skip_check:
				break
			val = tuple(getattr(obj, field) for field in check)
			if val in self.unique_values[check]:
				unique_errors.update(check)
		return unique_errors

	def write_unique(self, obj):
		for check in self._meta.unique_checks:
			val = tuple(getattr(obj, field) for field in check)
			self.unique_values[check].add(val)

	def generate(self, command=None):
		bulk = []
		for obj in self:
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

	def done(self):
		pass
