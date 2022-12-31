# -*- coding: utf-8 -*-
from .models import NotRegistered
from django_sample_generator import generator


class NotRegisteredGenerator(generator.ModelGenerator):
	class Meta:
		model = NotRegistered


generators = [NotRegisteredGenerator(1)]
