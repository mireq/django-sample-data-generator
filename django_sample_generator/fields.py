# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import inspect
import copy

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

	def __init__(self, function=None, args=None, kwargs=None, *arg, **kwarg):
		super(FunctionFieldGenerator, self).__init__(*arg, **kwarg)
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
	def make_instance(*arg, **kwarg):
		kwarg = copy.copy(kwarg)
		kwarg.setdefault('function', function)
		kwarg.setdefault('args', args)
		kwarg.setdefault('kwargs', kwargs)
		return FunctionFieldGenerator(*arg, **kwarg)
	return make_instance


IntegerFieldGenerator = function_field_generator_factory(function=functions.gen_integer)
SeqIntegerFieldGenerator = function_field_generator_factory(function=functions.gen_seq_integer)
DateFieldGenerator = function_field_generator_factory(function=functions.gen_date)
DateTimeFieldGenerator = function_field_generator_factory(function=functions.gen_datetime)
CharFieldGenerator = function_field_generator_factory(function=functions.gen_varchar)
TextFieldGenerator = function_field_generator_factory(function=functions.gen_text_paragraph)
ForeignKeyFieldGenerator = function_field_generator_factory(function=functions.gen_fk)
EmailFieldGenerator = function_field_generator_factory(function=functions.gen_email)
BooleanFieldGenerator = function_field_generator_factory(function=functions.gen_bool)
