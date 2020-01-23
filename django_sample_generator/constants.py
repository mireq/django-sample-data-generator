# -*- coding: utf-8 -*-
TEXT_START = ''
SENTENCE_END = ['.', '?', '!']
WORD_END = '\0'
SPECIAL_TOKENS = set(SENTENCE_END + [TEXT_START, WORD_END, ','])
