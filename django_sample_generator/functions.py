# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import random
import string
import time
from datetime import datetime, timedelta

from django.template.defaultfilters import slugify
from django.utils.timezone import datetime as tz_datetime, utc

from .text_generator import text_generator


MAX_INT = 10000


def today_add_days(days):
	return datetime.now().date() + timedelta(days)


def now_add_days(days):
	return datetime.now() + timedelta(days)


def gen_integer(min_int=-MAX_INT, max_int=MAX_INT):
	return random.randint(min_int, max_int)


def gen_seq_integer(start=1, step=1):
	for i in itertools.count(start, step):
		yield i


def gen_date(min_date=today_add_days(-365), max_date=today_add_days(365)):
	min_date = time.mktime(min_date.timetuple())
	max_date = time.mktime(max_date.timetuple())
	for __ in itertools.count():
		random_time = min_date + random.random() * (max_date - min_date)
		yield tz_datetime.fromtimestamp(time.mktime(time.localtime(random_time))).date()


def gen_datetime(min_date=now_add_days(-365), max_date=now_add_days(365)):
	min_date = time.mktime(min_date.timetuple())
	max_date = time.mktime(max_date.timetuple())
	for __ in itertools.count():
		random_time = min_date + random.random() * (max_date - min_date)
		yield tz_datetime.fromtimestamp(time.mktime(time.localtime(random_time))).replace(tzinfo=utc)


def trim_text(text, max_length=None):
	if not text:
		return text
	if max_length is None:
		return text
	else:
		return text[:max_length]


def gen_varchar(max_length=None, blank=False):
	length = random.randint(0 if blank else 1, 16 if max_length is None else max_length)
	chars = string.printable
	if length:
		return ''.join(random.choice(chars) for _ in range(length))
	else:
		return ''


def gen_slug(max_length=None, blank=False):
	length = random.randint(0 if blank else 1, 16 if max_length is None else max_length)
	chars = string.ascii_letters.lower()
	if length:
		return ''.join(random.choice(chars) for _ in range(length))
	else:
		return ''


def gen_text_word(uppercase_word=False, max_length=None):
	return trim_text(text_generator.get_word(uppercase_word), max_length)


def gen_text_name(uppercase_word=False, max_length=None):
	return trim_text(text_generator.get_word(uppercase_word, min_length=2), max_length)


def gen_text_sentence(max_length=None):
	return trim_text(text_generator.get_sentence(), max_length)


def gen_text_paragraph(sentence_count=None, max_length=None):
	return trim_text(text_generator.get_paragraph(sentence_count), max_length)


def gen_text_long(paragraph_count=None, max_length=None):
	return trim_text(text_generator.get_text(paragraph_count), max_length)


def gen_fk(queryset, random_data=True):
	instances = list(queryset)
	if not instances:
		return None
	for i in itertools.count():
		if random_data:
			yield random.choice(instances)
		else:
			yield instances[i % len(instances)]


def gen_email():
	return ''.join(gen_text_word() for _ in range(3)) + '@' + slugify(''.join(gen_text_word() for _ in range(2))) + '.com'


def gen_url():
	return 'http://' + gen_text_word() + '.' + slugify(''.join(gen_text_word() for _ in range(2))) + '.com'


def gen_bool(true_rate=50):
	num = random.randrange(0, 100)
	return num < true_rate


def gen_choice(choices):
	return random.choice(choices)


def gen_seq_choice(choices):
	for choice in choices:
		yield choice
