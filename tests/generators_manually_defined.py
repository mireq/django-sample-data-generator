# -*- coding: utf-8 -*-
from .models import Article, Category
from django_sample_generator import generator, fields


class CategoryGenerator(generator.ModelGenerator):
	char_field = fields.CharFieldGenerator()

	def get_object(self):
		obj = super().get_object()
		obj.name = obj.char_field
		return obj

	class Meta:
		model = Category
		fields = ['slug']


class ArticleGenerator(generator.ModelGenerator):
	category = fields.ForeignKeyFieldGenerator(
		random_data=False,
		queryset=Category.objects.order_by('pk').only('pk')
	)
	category_field = fields.ForeignKeyFieldGenerator(
		random_data=False,
		queryset=Category.objects.order_by('pk').only('pk')
	)

	def get_object(self):
		obj = super().get_object()
		obj.category = obj.category_field
		return obj

	class Meta:
		model = Article
		fields = ['slug']


generators = [
	CategoryGenerator(5),
	ArticleGenerator(5),
]
