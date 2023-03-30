# -*- coding: utf-8 -*-
import array
import os
import pickle
import random
from io import StringIO
from itertools import chain

from .constants import TEXT_START, SENTENCE_END, WORD_END, SPECIAL_TOKENS


class TextGenerator(object):
	def __init__(self, token_list, token_transitions):
		self.token_list = tuple(token_list)
		self.token_transitions = token_transitions
		self.token_list_search = {s: i for i, s in enumerate(self.token_list) if s in SPECIAL_TOKENS}
		self.stop_tokens = set([self.token_list_search[w] for w in (SENTENCE_END + [WORD_END])])
		self.token_transitions_idx = tuple(array.array('L', chain(*[[v[0]] * v[1] for v in val])) for val in self.token_transitions)
		self.word_end = self.token_list_search[WORD_END]
		self.text_start = self.token_list_search[TEXT_START]

	def __generate_word(self, min_length=1):
		word = StringIO()
		current_part = self.text_start
		while True:
			parts = self.token_transitions_idx[current_part]
			current_part = random.choice(parts)

			# check if it's end of word
			if current_part in self.stop_tokens:
				# ensure, that word has a minimal length
				if word.tell() >= min_length:
					word.write(self.token_list[current_part])
					break
				else:
					current_part = self.text_start
					continue

			# write current part
			word.write(self.token_list[current_part])
		return word.getvalue()

	def get_word(self, uppercase=False, include_stops=False, min_length=1):
		word = self.__generate_word(min_length=min_length)
		if not include_stops and word[-1:] in SPECIAL_TOKENS:
			word = word[:-1]
		word = word.replace('\0', ' ')
		if uppercase:
			word = word.title()
		return word

	def get_sentence(self):
		words = StringIO()
		word = ''
		while word[-1:] not in set(SENTENCE_END):
			word = self.get_word(uppercase=words.tell() == 0, include_stops=True)
			words.write(word)
		return words.getvalue()

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
