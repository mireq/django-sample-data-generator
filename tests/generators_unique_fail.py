# -*- coding: utf-8 -*-
from .models import UniqueTogether
from django_sample_generator import generator, fields


class UniqueTogetherGenerator(generator.ModelGenerator):
	foo = fields.SeqChoiceFieldGenerator(choices=[0, 0, 1] + [1] * 1000)
	bar = fields.SeqChoiceFieldGenerator(choices=[0, 0, 1] + [1] * 1000)

	class Meta:
		model = UniqueTogether


class UniquePartialGenerator(generator.ModelGenerator):
	foo = fields.SeqChoiceFieldGenerator(choices=[0, 1, 1])
	bar = fields.SeqChoiceFieldGenerator(choices=[0, 0, 1])

	class Meta:
		model = UniqueTogether


generators = []
test_generators = {
	'unique_together': [UniqueTogetherGenerator(2)],
	'unique_partial': [UniquePartialGenerator(2)],
}

def set_test(test):
	generators.clear()
	generators.extend(test_generators[test])
