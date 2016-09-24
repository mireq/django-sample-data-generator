# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_sample_generator import generator, fields, functions
from django.template.defaultfilters import slugify

from .models import Category, Article


def unique_slugify(text, slugs, trim=16):
	original_slug = slugify(text)[:trim]
	slug = original_slug
	i = 1
	while slug in slugs:
		slug = '%s-%d' % (original_slug, i)
		i += 1
	slugs.add(slug)
	return slug


class CategoryGenerator(generator.ModelGenerator):
	class Meta:
		model = Category
		field_kwargs = {
			'slug': {'max_length': 2},
		}


class ArticleGenerator(generator.ModelGenerator):
	content = fields.function_field_generator(functions.gen_text_long)

	class Meta:
		model = Article
		exclude = ('slug',)

	def get_object(self):
		obj = super(ArticleGenerator, self).get_object()
		obj.slug = unique_slugify(obj.title, self.unique_values['slug'])
		return obj


generators = [
	CategoryGenerator(10),
	ArticleGenerator(100),
]
