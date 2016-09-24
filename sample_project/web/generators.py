# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_sample_generator import generator, fields, functions

from .models import Category, Article


class CategoryGenerator(generator.ModelGenerator):
	class Meta:
		model = Category
		field_kwargs = { # TODO: implement
			'slug': {'max_length': 2},
		}


class ArticleGenerator(generator.ModelGenerator):
	content = fields.function_field_generator(functions.gen_text_long)

	class Meta:
		model = Article
		exclude = ('slug',)


generators = [
	CategoryGenerator(10),
	ArticleGenerator(100),
]
