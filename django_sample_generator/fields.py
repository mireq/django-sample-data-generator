# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import inspect
import itertools

from django.db import models
from django.utils import six

from . import functions


class FieldGenerator(object):
	field = None

	def __iter__(self):
		for __ in itertools.count():
			yield self.get_value()

	def get_value(self):
		raise NotImplementedError()


class FunctionFieldGeneratorBase(type):
	def __new__(cls, name, bases, attrs):
		fn = attrs.pop('function', None)
		new_class = super(FunctionFieldGeneratorBase, cls).__new__(cls, name, bases, attrs)
		if fn:
			new_class.function = staticmethod(fn)
		else:
			new_class.function = fn
		return new_class


class FunctionFieldGenerator(six.with_metaclass(FunctionFieldGeneratorBase, FieldGenerator)):
	function = None
	function_kwargs = {}

	def __init__(self, function=None, **kwargs):
		super(FunctionFieldGenerator, self).__init__()
		self.function = function or self.function
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

	def get_function_kwargs(self):
		return self.function_kwargs

	def get_value(self):
		return self.get_function()(**self.get_function_kwargs())


class BinaryFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_binary


class BooleanFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_bool


class CharFieldGenerator(FunctionFieldGenerator):
	def get_function(self):
		if not self.field:
			return functions.gen_varchar
		else:
			if self.field.choices:
				return functions.gen_choice
			else:
				return functions.gen_varchar

	def get_function_kwargs(self):
		kwargs = super(CharFieldGenerator, self).get_function_kwargs()
		if not self.field:
			return kwargs
		if self.field.choices:
			kwargs.setdefault('choices', [k for k, _ in self.field.choices])
		else:
			kwargs.setdefault('max_length', min(self.field.max_length, 255))
		return kwargs


class ChoiceFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_choice


class DateFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_date


class DateTimeFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_datetime


class DurationFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_duration


class EmailFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_email


class ForeignKeyFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_fk

	def get_function_kwargs(self):
		kwargs = super(ForeignKeyFieldGenerator, self).get_function_kwargs()
		if not self.field:
			return kwargs
		kwargs.setdefault('queryset', self.field.rel.model._default_manager.only('pk'))
		return kwargs


class LongTextFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_long


class IntegerFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_integer


class SeqIntegerFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_seq_integer


class SlugFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_slug


class TextFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_paragraph


GENERATOR_FOR_DBFIELD = {
	models.BigIntegerField: IntegerFieldGenerator,
	models.BinaryField: BinaryFieldGenerator,
	models.BooleanField: BooleanFieldGenerator,
	models.CharField: CharFieldGenerator,
	models.DateField: DateFieldGenerator,
	models.DateTimeField: DateTimeFieldGenerator,
	models.DecimalField: IntegerFieldGenerator,
	models.DurationField: DurationFieldGenerator,
	models.ForeignKey: ForeignKeyFieldGenerator,
	models.SlugField: SlugFieldGenerator,
	models.TextField: TextFieldGenerator,
}
