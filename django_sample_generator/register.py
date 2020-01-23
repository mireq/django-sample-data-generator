# -*- coding: utf-8 -*-
class GeneratorRegister(object):
	def __init__(self):
		self.generators = []

	def register(self, obj):
		self.generators.append(obj)

	def generate(self, command=None):
		for generator in self.generators:
			if command is not None and command.verbosity > 1:
				command.stdout.write('\nGenerating ' + generator.__class__.__name__ + ' ', ending='')
				command.stdout.flush()
			generator.generate(command)
			generator.done()
