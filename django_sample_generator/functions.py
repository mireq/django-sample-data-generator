# -*- coding: utf-8 -*-
import itertools
import os
import random
import string
import time
from datetime import timedelta, datetime, timezone

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.timezone import datetime as tz_datetime, now

from .text_generator import get_text_generator


MAX_INT = 10000


def today_add_days(days):
	return datetime.now().date() + timedelta(days)


def now_add_days(days):
	return datetime.now() + timedelta(days)


def trim_text(text, max_length=None):
	if not text:
		return text
	if max_length is None:
		return text
	else:
		return text[:max_length]


def gen_integer(min_int=-MAX_INT, max_int=MAX_INT):
	return random.randint(min_int, max_int)


def gen_float():
	return (random.random() / (random.random() or 1.0)) * 1000.0


def gen_ip():
	return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def gen_seq_integer(start=1, step=1):
	yield from itertools.count(start, step)


def gen_date(min_date=today_add_days(-365), max_date=today_add_days(0)):
	min_date = time.mktime(min_date.timetuple())
	max_date = time.mktime(max_date.timetuple())
	while True:
		random_time = min_date + random.random() * (max_date - min_date)
		yield tz_datetime.fromtimestamp(time.mktime(time.localtime(random_time))).date()


def gen_datetime(min_date=now_add_days(-365), max_date=now_add_days(0)):
	min_date = time.mktime(min_date.timetuple())
	max_date = time.mktime(max_date.timetuple())
	while True:
		random_time = min_date + random.random() * (max_date - min_date)
		if settings.USE_TZ:
			yield tz_datetime.fromtimestamp(time.mktime(time.localtime(random_time))).replace(tzinfo=timezone.utc)
		else:
			yield tz_datetime.fromtimestamp(time.mktime(time.localtime(random_time)))


def gen_duration(min_duration=0, max_duration=3600):
	return timedelta(seconds=random.randint(min_duration, max_duration))


def gen_varchar(max_length=None, blank=False):
	length = random.randint(0 if blank else 1, 16 if max_length is None else max_length)
	chars = string.ascii_letters + string.digits + ' '
	if length:
		return ''.join(random.choice(chars) for _ in range(length))
	else:
		return ''


def gen_binary(min_length=1, max_length=16):
	length = random.randint(min_length, max_length)
	return bytearray([random.randint(0, 255) for _ in range(length)])


def gen_random_lowercase_str(min_length, max_length):
	length = random.randint(min_length, max_length)
	return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def gen_slug(max_length=None, blank=False):
	length = random.randint(0 if blank else 1, 16 if max_length is None else max_length)
	chars = string.ascii_lowercase
	if length:
		return ''.join(random.choice(chars) for _ in range(length))
	else:
		return ''


def gen_text_word(uppercase_word=False, max_length=None):
	return trim_text(get_text_generator().get_word(uppercase_word), max_length)


def gen_text_name(uppercase_word=False, max_length=None):
	return trim_text(get_text_generator().get_word(uppercase_word, min_length=2), max_length)


def gen_text_sentence(max_length=None):
	return trim_text(get_text_generator().get_sentence(), max_length)


def gen_text_paragraph(sentence_count=None, max_length=None):
	return trim_text(get_text_generator().get_paragraph(sentence_count), max_length)


def gen_text_long(paragraph_count=None, max_length=None):
	return trim_text(get_text_generator().get_text(paragraph_count), max_length)


def gen_fk(queryset, random_data=True):
	instances = list(queryset)
	if random_data:
		while True:
			yield random.choice(instances)
	else:
		i = 0
		while True:
			yield instances[i % len(instances)]
			i += 1


def gen_email():
	return '%s@%s.%s' % (gen_random_lowercase_str(6, 10), gen_random_lowercase_str(6, 10), gen_random_lowercase_str(2, 3))


def gen_url():
	return 'http://%s.%s' % (gen_random_lowercase_str(8, 12), gen_random_lowercase_str(2, 3))


def gen_bool(true_rate=50):
	num = random.randrange(0, 100)
	return num < true_rate


def gen_choice(choices):
	return random.choice(choices)


def gen_seq_choice(choices):
	yield from iter(choices)


def gen_time():
	return now() + timedelta(seconds=random.randint(-3600*24, 0))


def gen_uuid():
	import uuid
	return uuid.uuid4()


def gen_file(file_name):
	path = os.path.join(os.path.dirname(__file__), file_name)
	with open(path, 'rb') as f:
		return ContentFile(f.read(), file_name)
