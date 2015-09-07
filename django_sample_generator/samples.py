# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import pickle
import random
import time
from datetime import datetime, timedelta
from itertools import chain

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.utils.timezone import datetime as tz_datetime, utc

from .constants import TEXT_START, SENTENCE_END, WORD_END, SPECIAL_TOKENS


class Sample(object):
	def __init__(self, count=0, unique=False):
		self.count = count
		self.num = 0
		self.unique = unique
		self.generated_values = set()

	def __iter__(self):
		return self

	def get_sample(self):
		raise NotImplementedError()

	def next(self):
		if self.num < self.count:
			self.num += 1
			if self.unique:
				for sample in self.__generate_sample():
					if not sample in self.generated_values:
						self.generated_values.add(sample)
						return sample
			else:
				return self.get_sample()
		else:
			raise StopIteration()

	def __generate_sample(self):
		while True:
			yield self.get_sample()


class TextGenerator(object):
	def __init__(self, token_list, token_transitions):
		self.token_list = token_list
		self.token_transitions = token_transitions
		self.token_list_search = {s: i for i, s in enumerate(self.token_list) if s in SPECIAL_TOKENS}
		self.stop_tokens = set([self.token_list_search[w] for w in (SENTENCE_END + [WORD_END])])
		self.token_transitions_idx = tuple(tuple(chain(*[[v[0]] * v[1] for v in val])) for val in self.token_transitions)

	def __generate_word(self):
		word = []
		current_part = self.token_list_search[TEXT_START]
		stop = self.token_list_search[WORD_END]
		while current_part not in self.stop_tokens:
			parts = self.token_transitions_idx[current_part]
			current_part = parts[random.randrange(0, len(parts))]
			if current_part != stop:
				word.append(self.token_list[current_part])
		return ''.join(word)

	def get_word(self, uppercase=False, include_stops=False, min_length=1):
		word = ''
		while len(word) < min_length:
			word = self.__generate_word()
		if not include_stops and word[-1] in SPECIAL_TOKENS:
			word = word[:-1]
		if uppercase:
			if len(word) > 1:
				word = word[0].upper() + word[1:]
			else:
				word = word.upper()
		return word

	def get_sentence(self):
		words = []
		word = ''
		while word[-1:] not in set(SENTENCE_END):
			word = self.get_word(uppercase=len(words) == 0, include_stops=True)
			words.append(word)
		return ' '.join(words)

	def get_paragraph(self, length=None):
		paragraph = []
		if length is None:
			length = int(random.expovariate(.25) + random.randint(5, 10))
		return ' '.join(self.get_sentence() for _ in range(length))

	def get_text(self, length=None):
		paragraphs = []
		if length is None:
			length = int(random.expovariate(.25) + random.randint(5, 10))
		return '\n'.join(self.get_paragraph() for _ in range(length))

	@staticmethod
	def from_file(filename):
		token_list, token_transitions = pickle.load(open(filename, 'rb'))
		return TextGenerator(token_list, token_transitions)


class NumberSample(Sample):
	def __init__(self, random_data=True, min_value=0, max_value=100, **kwargs):
		super(NumberSample, self).__init__(**kwargs)
		self.random = random_data
		self.min_value = min_value
		self.max_value = max_value
		if self.random:
			pass
		else:
			self.current_value = min_value

	def get_sample(self):
		if self.random:
			ret = random.randrange(self.min_value, self.max_value)
		else:
			ret = self.current_value
			self.current_value += 1
		return ret


class DateSample(Sample):
	def __init__(self, min_date=datetime.now().date() - timedelta(365), max_date=datetime.now().date(), **kwargs):
		super(DateSample, self).__init__(**kwargs)
		self.min_date = time.mktime(min_date.timetuple())
		self.max_date = time.mktime(max_date.timetuple())

	def get_sample(self):
		return tz_datetime.fromtimestamp(time.mktime(time.localtime(self.min_date + random.random() * (self.max_date - self.min_date)))).date()


class DateTimeSample(Sample):
	def __init__(self, min_date=datetime.now() - timedelta(365), max_date=datetime.now(), **kwargs):
		super(DateTimeSample, self).__init__(**kwargs)
		self.min_date = time.mktime(min_date.timetuple())
		self.max_date = time.mktime(max_date.timetuple())

	def get_sample(self):
		return tz_datetime.fromtimestamp(time.mktime(time.localtime(self.min_date + random.random() * (self.max_date - self.min_date)))).replace(tzinfo=utc)


class TextSample(Sample):
	Word = 0
	Name = 1
	Sentence = 2
	Paragraph = 3
	Text = 4

	def __init__(self, text_type, max_length=None, **kwargs):
		super(TextSample, self).__init__(**kwargs)
		self.text_type = text_type
		self.max_length = max_length # výstup nikdy nepresiahne túto hodnotu
		self.uppercase_word = False # prvý znak slova veľkými
		self.paragraph_length = None # počet viet v odstavci
		self.text_length = None # počet odstavcov v texte
		self.generator = TextGenerator.from_file(os.path.join(os.path.dirname(__file__), 'text_db'))

	def get_sample(self):
		if self.text_type == self.Word:
			data = self.generator.get_word(self.uppercase_word)
		if self.text_type == self.Name:
			data = self.generator.get_word(self.uppercase_word, min_length=2)
		elif self.text_type == self.Sentence:
			data = self.generator.get_sentence()
		elif self.text_type == self.Paragraph:
			data = self.generator.get_paragraph(self.paragraph_length)
		elif self.text_type == self.Text:
			data = self.generator.get_text(self.text_length)
		if self.max_length:
			data = data[:self.max_length - 1]
		return data


class WordSample(TextSample):
	def __init__(self, uppercase_word=False, max_length=None, **kwargs):
		super(WordSample, self).__init__(TextSample.Word, max_length, **kwargs)
		self.uppercase_word = uppercase_word


class NameSample(TextSample):
	def __init__(self, uppercase_word=True, max_length=None, **kwargs):
		super(NameSample, self).__init__(TextSample.Name, max_length, **kwargs)
		self.uppercase_word = uppercase_word


class SentenceSample(TextSample):
	def __init__(self, sentence_length=None, max_length=None, **kwargs):
		super(SentenceSample, self).__init__(TextSample.Sentence, max_length, **kwargs)
		self.sentence_length = sentence_length


class ParagraphSample(TextSample):
	def __init__(self, paragraph_length=None, max_length=None, **kwargs):
		super(ParagraphSample, self).__init__(TextSample.Paragraph, max_length, **kwargs)
		self.paragraph_length = paragraph_length


class LongTextSample(TextSample):
	def __init__(self, text_length=None, max_length=None, **kwargs):
		super(LongTextSample, self).__init__(TextSample.Text, max_length, **kwargs)
		self.text_length = text_length


class RelationSample(Sample):
	def __init__(self, queryset, fetch_all=False, only_pk=False, random_data=True, **kwargs):
		super(RelationSample, self).__init__(**kwargs)
		self.only_pk = only_pk
		self.random_data = random_data
		self.fetch_all = fetch_all
		self.queryset = queryset

	def get_sample(self):
		if self.fetch_all:
			if self.only_pk and not hasattr(self, "pk_list"):
				setattr(self, "pk_list", [i.pk for i in self.queryset])
			elif type(self.queryset) != list:
				self.queryset = list(self.queryset)

		if self.only_pk and hasattr(self, "pk_list"):
			qs = getattr(self, "pk_list")
		else:
			qs = self.queryset

		if self.random_data:
			obj = qs[random.randrange(0, len(self.queryset))]
		else:
			obj = qs[self.num]
			self.num += 1

		if self.only_pk:
			if isinstance(obj, models.Model):
				return obj.pk
			else:
				return obj
		else:
			return obj


class EmailSample(Sample):
	def __init__(self, **kwargs):
		super(EmailSample, self).__init__(**kwargs)
		self.num = 0
		self.emails = set()
		self.text = TextSample(text_type=TextSample.Word)

	def get_sample(self):
		self.num += 1
		while 1:
			email = slugify(self.text.get_sample() + self.text.get_sample() + self.text.get_sample()) + "@" + slugify(self.text.get_sample()) + ".com"
			if not email in self.emails:
				self.emails.add(email)
				break
		return email


class RandomItemSample(Sample):
	def __init__(self, items, **kwargs):
		super(RandomItemSample, self).__init__(**kwargs)
		self.items = list(items)

	def get_sample(self):
		return self.items[random.randrange(0, len(self.items))]


class RandomStringSample(Sample):
	def get_sample(self):
		return get_random_string()


class PointSample(Sample):
	def get_sample(self):
		return "SRID=3857;POINT({0} {1})".format(random.randint(1800000, 2500000), random.randint(5800000, 6500000))


class PhoneNumberSample(Sample):
	def get_sample(self):
		return "+421908{0:06d}".format(random.randint(0, 1000000))


class URLSample(Sample):
	def __init__(self, **kwargs):
		super(URLSample, self).__init__(**kwargs)
		self.text = TextSample(text_type=TextSample.Word)

	def get_sample(self):
		self.num += 1
		return "http://" + slugify(self.text.get_sample()) + "." + slugify(self.text.get_sample()) + ".com"


class BooleanSample(Sample):
	def __init__(self, true_rate=50):
		super(BooleanSample, self).__init__()
		self.true_rate = true_rate

	def get_sample(self):
		num = random.randrange(0, 100)
		return num < self.true_rate
