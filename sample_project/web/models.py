# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=20, unique=True)


class Article(models.Model):
	category = models.ForeignKey(Category)
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=20, unique=True)
	perex = models.TextField()
	content = models.TextField()
