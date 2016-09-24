# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_sample_generator import generator

from .models import Category


class CategoryGenerator(generator.ModelGenerator):
	class Meta:
		model = Category


generators = [
	CategoryGenerator(10),
]
