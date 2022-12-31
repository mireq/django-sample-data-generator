# -*- coding: utf-8 -*-
import copy
import inspect

from django.db import models

from . import functions


class FieldGenerator(object):
	field = None

	def __iter__(self):
		while True:
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


class FunctionFieldGenerator(FieldGenerator, metaclass=FunctionFieldGeneratorBase):
	function = None
	function_kwargs = {}

	def __init__(self, function=None, **kwargs):
		super().__init__()
		self.function = function or self.function
		self.function_kwargs = copy.copy(self.function_kwargs)
		self.function_kwargs.update(kwargs)

	def __iter__(self):
		if inspect.isgeneratorfunction(self.get_function()):
			yield from self.get_value()
		else:
			while True:
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
		kwargs = super().get_function_kwargs()
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


class FileFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_file
	function_kwargs = {'file_name': 'mock.txt'}


class FloatFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_float


class ForeignKeyFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_fk

	def get_function_kwargs(self):
		kwargs = super().get_function_kwargs()
		if not self.field:
			return kwargs
		if not 'queryset' in kwargs:
			kwargs['queryset'] = self.field.remote_field.model._default_manager.only('pk')
		return kwargs


class LongTextFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_long


class ImageFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_file
	function_kwargs = {'file_name': 'mock.png'}


class IntegerFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_integer


class IPAddressFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_ip


class PositiveIntegerFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_integer
	function_kwargs = {'min_int': 1}


class SeqIntegerFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_seq_integer


class SeqChoiceFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_seq_choice


class SlugFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_slug


class WordFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_word


class NameFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_name


class SentenceFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_sentence


class TextFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_paragraph


class TimeFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_time


class URLFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_url


class UUIDFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_uuid


GENERATOR_FOR_DBFIELD = {
	models.BigIntegerField: IntegerFieldGenerator,
	models.BinaryField: BinaryFieldGenerator,
	models.BooleanField: BooleanFieldGenerator,
	models.CharField: CharFieldGenerator,
	models.DateField: DateFieldGenerator,
	models.DateTimeField: DateTimeFieldGenerator,
	models.DecimalField: IntegerFieldGenerator,
	models.DurationField: DurationFieldGenerator,
	models.EmailField: EmailFieldGenerator,
	models.FileField: FileFieldGenerator,
	models.FloatField: FloatFieldGenerator,
	models.ForeignKey: ForeignKeyFieldGenerator,
	models.GenericIPAddressField: IPAddressFieldGenerator,
	models.IPAddressField: IPAddressFieldGenerator,
	models.IntegerField: IntegerFieldGenerator,
	models.ImageField: ImageFieldGenerator,
	models.NullBooleanField: BooleanFieldGenerator,
	models.PositiveIntegerField: PositiveIntegerFieldGenerator,
	models.PositiveSmallIntegerField: PositiveIntegerFieldGenerator,
	models.SlugField: SlugFieldGenerator,
	models.SmallIntegerField: IntegerFieldGenerator,
	models.TextField: TextFieldGenerator,
	models.TimeField: TimeFieldGenerator,
	models.URLField: URLFieldGenerator,
	models.UUIDField: UUIDFieldGenerator,
}
