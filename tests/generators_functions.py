# -*- coding: utf-8 -*-
from .models import Foo
from django_sample_generator import generator, fields


class BlankTextGenerator(generator.ModelGenerator):
	field = fields.CharFieldGenerator(blank=True, max_length=0)

	class Meta:
		model = Foo


class BlankSlugGenerator(generator.ModelGenerator):
	field = fields.SlugFieldGenerator(blank=True, max_length=0)

	class Meta:
		model = Foo


class SeqIntegerGenerator(generator.ModelGenerator):
	field = fields.SeqIntegerFieldGenerator(start=10, step=5)

	class Meta:
		model = Foo


generators = []
test_generators = {
	'blank': [BlankTextGenerator(1)],
	'blank_slug': [BlankSlugGenerator(1)],
	'seq': [SeqIntegerGenerator(2)],
}


def set_test(test):
	generators.clear()
	generators.extend(test_generators[test])
