# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import inspect
import copy

from django.db import models

from . import functions


class FieldGenerator(object):
	def __iter__(self):
		for __ in itertools.count():
			yield self.get_value()

	def get_value(self):
		raise NotImplementedError()


class FunctionFieldGenerator(FieldGenerator):
	function = None
	function_args = []
	function_kwargs = {}

	def __init__(self, function=None, *args, **kwargs):
		super(FunctionFieldGenerator, self).__init__()
		self.function = function or self.function
		self.function_args = args or []
		self.function_kwargs = kwargs or {}

	def __iter__(self):
		if inspect.isgeneratorfunction(self.get_function()):
			for value in self.get_value():
				yield value
		else:
			for __ in itertools.count():
				yield self.get_value()

	def get_function(self):
		return self.function

	def get_function_args(self):
		return self.function_args

	def get_function_kwargs(self):
		return self.function_kwargs

	def get_value(self):
		return self.get_function()(*self.get_function_args(), **self.get_function_kwargs())


def function_field_generator_factory(function=None, args=None, kwargs=None):
	def make_instance(*args, **kwargs):
		return FunctionFieldGenerator(function=function, *args, **kwargs)
	return make_instance


def function_field_generator(function, **kwargs):
	return function_field_generator_factory(function)(**kwargs)


BinaryFieldGenerator = function_field_generator_factory(function=functions.gen_binary)
BooleanFieldGenerator = function_field_generator_factory(function=functions.gen_bool)
CharFieldGenerator = function_field_generator_factory(function=functions.gen_varchar)
ChoiceFieldGenerator = function_field_generator_factory(function=functions.gen_choice)
DateFieldGenerator = function_field_generator_factory(function=functions.gen_date)
DateTimeFieldGenerator = function_field_generator_factory(function=functions.gen_datetime)
DurationFieldGenerator = function_field_generator_factory(function=functions.gen_duration)
EmailFieldGenerator = function_field_generator_factory(function=functions.gen_email)
ForeignKeyFieldGenerator = function_field_generator_factory(function=functions.gen_fk)
IntegerFieldGenerator = function_field_generator_factory(function=functions.gen_integer)
SeqIntegerFieldGenerator = function_field_generator_factory(function=functions.gen_seq_integer)
SlugFieldGenerator = function_field_generator_factory(function=functions.gen_slug)
TextFieldGenerator = function_field_generator_factory(function=functions.gen_text_paragraph)


def generator_field_with_defaults(generator, default=None, **kwargs):
	kw = copy.copy(default) or {}
	kw.update(kwargs)
	return generator(**kw)


def get_char_field_generator(field, **kwargs):
	if field.choices:
		return generator_field_with_defaults(
			ChoiceFieldGenerator,
			default={'choices': [k for k, _ in field.choices]},
			**kwargs
		)
	else:
		return generator_field_with_defaults(
			CharFieldGenerator,
			default={'max_length': min(field.max_length, 255)},
			**kwargs
		)


def get_foreign_key_generator(field, **kwargs):
	return generator_field_with_defaults(
		ForeignKeyFieldGenerator,
		default={'queryset': field.rel.model._default_manager.only('pk')},
		**kwargs
	)


GENERATOR_FOR_DBFIELD = {
	models.BigIntegerField:
		lambda field, **kwargs: IntegerFieldGenerator(**kwargs),
	models.BinaryField:
		lambda field, **kwargs: BinaryFieldGenerator(**kwargs),
	models.BooleanField:
		lambda field, **kwargs: BooleanFieldGenerator(**kwargs),
	models.CharField:
		get_char_field_generator,
	models.DateField:
		lambda field, **kwargs: DateFieldGenerator(**kwargs),
	models.DateTimeField:
		lambda field, **kwargs: DateTimeFieldGenerator(**kwargs),
	models.DecimalField:
		lambda field, **kwargs: IntegerFieldGenerator(**kwargs),
	models.DurationField:
		lambda field, **kwargs: DurationFieldGenerator(**kwargs),
	models.ForeignKey:
		get_foreign_key_generator,
	models.SlugField:
		lambda field, **kwargs: SlugFieldGenerator(**kwargs),
	models.TextField:
		lambda field, **kwargs: TextFieldGenerator(**kwargs),
	#models.EmailField:
	#	lambda field, **kwargs: EmailFieldGenerator(**kwargs),
}
