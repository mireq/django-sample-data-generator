# -*- coding: utf-8 -*-
import uuid
from datetime import timedelta, time

from django.db import models
from django.utils import timezone


class Foo(models.Model):
	field = models.CharField(max_length=100)


class CustomField(models.CharField):
	pass


class NotRegistered(models.Model):
	field = CustomField(max_length=100)


class UniqueTogether(models.Model):
	foo = models.IntegerField()
	bar = models.IntegerField()

	class Meta:
		unique_together = [('foo', 'bar'), ('bar',)]


class Category(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=20, unique=True)

	class Meta:
		unique_together = [('slug', 'id'),]


class Article(models.Model):
	PUBLISHED_CHOICES = (
		('y', 'Published'),
		('n', 'Not published')
	)

	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=20, unique=True)
	perex = models.TextField()
	content = models.TextField()
	published = models.CharField(max_length=1, choices=PUBLISHED_CHOICES)

	# all fields
	big_integer_field = models.BigIntegerField(default=0)
	binary_field = models.BinaryField()
	boolean_fied = models.BooleanField(default=False)
	char_field = models.CharField(max_length=100)
	date_field = models.DateField(default=timezone.now)
	date_time_field = models.DateTimeField(default=timezone.now)
	decimal_field = models.DecimalField(max_digits=10, decimal_places=0, default=0)
	duration_field = models.DurationField(default=timedelta(0))
	email_field = models.EmailField(default='example@tld.com')
	file_field = models.FileField()
	float_field = models.FloatField(default=0)
	integer_field = models.IntegerField(default=0)
	image_field = models.ImageField()
	ip_address_field = models.GenericIPAddressField(default='127.0.0.1')
	null_boolean_field = models.BooleanField(null=True)
	positive_integer_field = models.PositiveIntegerField(default=0)
	positive_small_integer_field = models.PositiveSmallIntegerField(default=0)
	slug_field = models.SlugField()
	small_integer_field = models.SmallIntegerField(default=0)
	text_field = models.TextField(default='')
	time_field = models.TimeField(default=time(0))
	url_field = models.URLField(default='http://example.tld/')
	uuid_field = models.UUIDField(default=uuid.uuid4)
