# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import time
from datetime import datetime, timedelta

import random
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.utils.timezone import datetime as tz_datetime, utc


class Sample(object):
	def __init__(self, count = 0):
		self.count = count
		self.num = 0

	def __iter__(self):
		return self

	def get_sample(self):
		raise NotImplementedError()

	def next(self):
		if self.num < self.count:
			self.num += 1
			return self.get_sample()
		else:
			raise StopIteration()


class TextGenerator(object):
	SAMOHLASKA = 0
	SPOLUHLASKA = 1

	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(TextGenerator, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self):
		self.spluhlasky = set(['b', 'c', 'c', 'd', 'ď', 'f', 'g', 'h', 'j', 'k', 'l', 'ľ', 'm', 'n', 'ň', 'p', 'q', 'r', 'ŕ', 's', 'š', 't', 'ť', 'v', 'w', 'x', 'z', 'ž'])
		self.samohlasky = set(['a', 'á', 'e', 'é', 'i', 'í', 'o', 'ó', 'ô', 'u', 'ú', 'y', 'ý'])
		self.database = {}
		self.sum_words = None
		self.build_database()

	def build_database(self):
		fp = codecs.open(os.path.join(os.path.dirname(__file__), 'db.txt'), encoding="utf-8", mode='r')
		data = fp.read().split(' ')
		database = {}
		for word in data:
			hyph = word.split('-')
			if len(hyph) in database:
				subdatabase = database[len(hyph)]
			else:
				subdatabase = {'count': 0, 'subcount': [0, 0], 'data': {}}
				database[len(hyph)] = subdatabase
			subdatabase['count'] += 1
			data = subdatabase['data']
			for part in hyph:
				if not part in data:
					data[part] = 0
				data[part] += 1
				if len(part) > 0 and part[0] in self.samohlasky:
					subdatabase['subcount'][self.SAMOHLASKA] += 1
				else:
					subdatabase['subcount'][self.SPOLUHLASKA] += 1
		def sum_database_item():
			count_sum = [0, 0]
			def add_item(item):
				if len(item[0]) > 0 and item[0][0] in self.samohlasky:
					count_sum[self.SAMOHLASKA] += item[1]
					return (item[0], item[1] + count_sum[self.SAMOHLASKA])
				else:
					count_sum[self.SPOLUHLASKA] += item[1]
					return (item[0], item[1] + count_sum[self.SPOLUHLASKA])
			return add_item
		for length in database:
			data = database[length]['data']
			data = list(data.iteritems())
			sorted_data = sorted(data, key=lambda d: -d[1])
			sum_fun = sum_database_item()
			sorted_data = [sum_fun(i) for i in sorted_data]
			separated_data = [None, None]
			separated_data[self.SAMOHLASKA] = [i for i in sorted_data if len(i[0]) > 0 and i[0][0] in self.samohlasky]
			separated_data[self.SPOLUHLASKA] = [i for i in sorted_data if not(len(i[0]) > 0 and i[0][0]) in self.samohlasky]
			database[length]['data'] = separated_data
		self.database = database

	def get_word(self, uppercase=False, min_length=1):
		word = u''
		length = self.get_word_length(min_length)
		chartype = None
		for _ in range(length):
			word += self.get_random_word_part(self.database[length], chartype)
			if len(word) > 0 and word[-1] in self.samohlasky:
				chartype = self.SPOLUHLASKA
			else:
				chartype = self.SAMOHLASKA
		if uppercase:
			if len(word) > 1:
				word = word[0].upper() + word[1:]
			else:
				word = word.upper()
		return word

	def get_sentence(self, length=None):
		sentence = []
		if length is None:
			length = int(random.expovariate(.25) + random.randint(2, 8))
		old_word = ''
		for i in range(length):
			upper = True if i == 0 else False
			word = self.get_word(upper)
			while word == old_word or (len(word) == 1 and len(old_word) == 1):
				word = self.get_word(upper)
			sentence.append(word)
			old_word = word
		return u' '.join(sentence)

	def get_paragraph(self, length=None):
		paragraph = []
		if length is None:
			length = int(random.expovariate(.25) + random.randint(5, 10))
		for _ in range(length):
			paragraph.append(self.get_sentence() + '.')
		return u' '.join(paragraph)

	def get_text(self, length=5):
		return u"\n".join([self.get_paragraph() for _ in range(length)])

	def get_random_word_part(self, data, chartype=None):
		if chartype is None:
			rand = random.randint(0, data['subcount'][self.SAMOHLASKA] + data['subcount'][self.SPOLUHLASKA] - 1)
			if rand < data['subcount'][self.SAMOHLASKA]:
				chartype = self.SAMOHLASKA
			else:
				chartype = self.SPOLUHLASKA
		if data['subcount'][chartype] == 0:
			if chartype == self.SAMOHLASKA:
				chartype = self.SPOLUHLASKA
			else:
				chartype = self.SAMOHLASKA
		rand = random.randint(0, data['subcount'][chartype] - 1)
		strings = data['data'][chartype]
		for part in strings:
			if part[1] >= rand:
				return part[0]

	def get_word_length(self, min_length):
		if self.sum_words is None:
			self.sum_words = 0
			for length in self.database:
				self.sum_words += self.database[length]['count']
		rand = random.randint(0, self.sum_words - 1)
		count = 0
		for length in self.database:
			count += self.database[length]['count']
			if count >= rand:
				if length < min_length:
					return min_length
				else:
					return length


class NumberSample(Sample):
	def __init__(self, random_data=True, min_value=0, max_value=100):
		super(NumberSample, self).__init__()
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
	def __init__(self, min_date=datetime.now().date() - timedelta(365), max_date=datetime.now().date()):
		super(DateSample, self).__init__()
		self.min_date = time.mktime(min_date.timetuple())
		self.max_date = time.mktime(max_date.timetuple())

	def get_sample(self):
		return tz_datetime.fromtimestamp(time.mktime(time.localtime(self.min_date + random.random() * (self.max_date - self.min_date)))).date()


class DateTimeSample(Sample):
	def __init__(self, min_date=datetime.now() - timedelta(365), max_date=datetime.now()):
		super(DateTimeSample, self).__init__()
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

	def __init__(self, text_type, max_length=None):
		super(TextSample, self).__init__()
		self.text_type = text_type
		self.max_length = max_length # výstup nikdy nepresiahne túto hodnotu
		self.uppercase_word = False # prvý znak slova veľkými
		self.sentence_length = None #  počet slov vo vete
		self.paragraph_length = None # počet viet v odstavci
		self.text_length = None # počet odstavcov v texte
		self.generator = TextGenerator()

	def get_sample(self):
		if self.text_type == self.Word:
			data = self.generator.get_word(self.uppercase_word)
		if self.text_type == self.Name:
			data = self.generator.get_word(self.uppercase_word, 2)
		elif self.text_type == self.Sentence:
			data = self.generator.get_sentence(self.sentence_length)
		elif self.text_type == self.Paragraph:
			data = self.generator.get_paragraph(self.paragraph_length)
		elif self.text_type == self.Text:
			data = self.generator.get_text(self.text_length)
		if self.max_length:
			data = data[:self.max_length - 1]
		return data


class WordSample(TextSample):
	def __init__(self, uppercase_word=False, max_length=None):
		super(WordSample, self).__init__(TextSample.Word, max_length)
		self.uppercase_word = uppercase_word


class NameSample(TextSample):
	def __init__(self, uppercase_word=True, max_length=None):
		super(NameSample, self).__init__(TextSample.Name, max_length)
		self.uppercase_word = uppercase_word


class SentenceSample(TextSample):
	def __init__(self, sentence_length=None, max_length=None):
		super(SentenceSample, self).__init__(TextSample.Sentence, max_length)
		self.sentence_length = sentence_length


class ParagraphSample(TextSample):
	def __init__(self, paragraph_length=None, max_length=None):
		super(ParagraphSample, self).__init__(TextSample.Paragraph, max_length)
		self.paragraph_length = paragraph_length


class LongTextSample(TextSample):
	def __init__(self, text_length=None, max_length=None):
		super(LongTextSample, self).__init__(TextSample.Text, max_length)
		self.text_length = text_length


class RelationSample(Sample):
	def __init__(self, queryset, fetch_all=False, only_pk=False, random_data=True):
		super(RelationSample, self).__init__()
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
	def __init__(self):
		super(EmailSample, self).__init__()
		self.num = 0
		self.emails = set()
		self.text = TextSample(text_type = TextSample.Word)

	def get_sample(self):
		self.num += 1
		while 1:
			email = slugify(self.text.get_sample() + self.text.get_sample() + self.text.get_sample()) + "@" + slugify(self.text.get_sample()) + ".com"
			if not email in self.emails:
				self.emails.add(email)
				break
		return email


class RandomItemSample(Sample):
	def __init__(self, items):
		super(RandomItemSample, self).__init__()
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
	def __init__(self):
		super(URLSample, self).__init__()
		self.text = TextSample(text_type = TextSample.Word)

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
