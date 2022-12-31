# -*- coding: utf-8 -*-
from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=20, unique=True)


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
	big_integer_field = models.BigIntegerField()
	binary_field = models.BinaryField()
	boolean_fied = models.BooleanField()
	char_field = models.CharField(max_length=100)
	date_field = models.DateField()
	date_time_field = models.DateTimeField()
	decimal_field = models.DecimalField(max_digits=10, decimal_places=0)
	duration_field = models.DurationField()
	email_field = models.EmailField()
	file_field = models.FileField()
	float_field = models.FloatField()
	integer_field = models.IntegerField()
	image_field = models.ImageField()
	ip_address_field = models.GenericIPAddressField()
	null_boolean_field = models.BooleanField(null=True)
	positive_integer_field = models.PositiveIntegerField()
	positive_small_integer_field = models.PositiveSmallIntegerField()
	slug_field = models.SlugField()
	small_integer_field = models.SmallIntegerField()
	text_field = models.TextField()
	time_field = models.TimeField()
	url_field = models.URLField()
	uuid_field = models.UUIDField()
