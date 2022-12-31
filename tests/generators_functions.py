# -*- coding: utf-8 -*-
from .models import Foo
from django_sample_generator import generator, fields


class BlankTextGenerator(generator.ModelGenerator):
	field = fields.CharFieldGenerator(blank=True, max_length=0)


class BlankSlugGenerator(generator.ModelGenerator):
	field = fields.SlugFieldGenerator(blank=True, max_length=0)


class SeqIntegerGenerator(generator.ModelGenerator):
	field = fields.SeqIntegerFieldGenerator(start=10, step=5)


class TextGenerator(generator.ModelGenerator):
	field = fields.WordFieldGenerator(max_length=1)
	name = fields.NameFieldGenerator(max_length=5)
	sentence = fields.SentenceFieldGenerator(max_length=5)


class SeqChoiceGenerator(generator.ModelGenerator):
	field = fields.SeqChoiceFieldGenerator(choices=['A', 'B'])


class BulkGenerator(generator.ModelGenerator):
	bulk_size = 2
	field = fields.SeqIntegerFieldGenerator(start=1)


class Bulk2Generator(generator.ModelGenerator):
	bulk_size = 2
	field = fields.SeqIntegerFieldGenerator(start=1)


generators = []
test_generators = {
	'blank': [BlankTextGenerator(1, model=Foo)],
	'blank_slug': [BlankSlugGenerator(1, model=Foo)],
	'seq': [SeqIntegerGenerator(2, model=Foo)],
	'seq_choice': [SeqChoiceGenerator(2, model=Foo)],
	'text': [TextGenerator(1, model=Foo)],
	'bulk': [BulkGenerator(2, model=Foo)],
	'bulk2': [Bulk2Generator(3, model=Foo)],
}


def set_test(test):
	generators.clear()
	generators.extend(test_generators[test])
