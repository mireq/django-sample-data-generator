# -*- coding: utf-8 -*-
import os
import pickle
import random
from itertools import chain

from .constants import TEXT_START, SENTENCE_END, WORD_END, SPECIAL_TOKENS


class TextGenerator(object):
	def __init__(self, token_list, token_transitions):
		self.token_list = token_list
		self.token_transitions = token_transitions
		self.token_list_search = {s: i for i, s in enumerate(self.token_list) if s in SPECIAL_TOKENS}
		self.stop_tokens = set([self.token_list_search[w] for w in (SENTENCE_END + [WORD_END])])
		self.token_transitions_idx = tuple(tuple(chain(*[[v[0]] * v[1] for v in val])) for val in self.token_transitions)

	def __generate_word(self):
		word = []
		current_part = self.token_list_search[TEXT_START]
		stop = self.token_list_search[WORD_END]
		while current_part not in self.stop_tokens:
			parts = self.token_transitions_idx[current_part]
			current_part = parts[random.randrange(0, len(parts))]
			if current_part != stop:
				word.append(self.token_list[current_part])
		return ''.join(word)

	def get_word(self, uppercase=False, include_stops=False, min_length=1):
		word = ''
		while len(word) < min_length:
			word = self.__generate_word()
		if not include_stops and word[-1] in SPECIAL_TOKENS:
			word = word[:-1]
		if uppercase:
			if len(word) > 1:
				word = word[0].upper() + word[1:]
			else:
				word = word.upper()
		return word

	def get_sentence(self):
		words = []
		word = ''
		while word[-1:] not in set(SENTENCE_END):
			word = self.get_word(uppercase=len(words) == 0, include_stops=True)
			words.append(word)
		return ' '.join(words)

	def get_paragraph(self, length=None):
		if length is None:
			length = int(random.expovariate(.25) + random.randint(5, 10))
		return ' '.join(self.get_sentence() for _ in range(length))

	def get_text(self, length=None):
		if length is None:
			length = int(random.expovariate(.25) + random.randint(5, 10))
		return '\n'.join(self.get_paragraph() for _ in range(length))

	@staticmethod
	def from_file(filename):
		with open(filename, 'rb') as fp:
			token_list, token_transitions = pickle.load(fp)
		return TextGenerator(token_list, token_transitions)


def get_text_generator():
	if get_text_generator.generator is None:
		get_text_generator.generator = TextGenerator.from_file(os.path.join(os.path.dirname(__file__), 'text_db'))
	return get_text_generator.generator
get_text_generator.generator = None
