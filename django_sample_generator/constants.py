# -*- coding: utf-8 -*-
from __future__ import unicode_literals


TEXT_START = ''
SENTENCE_END = ['.', '?', '!']
WORD_END = '\0'
SPECIAL_TOKENS = set(SENTENCE_END + [TEXT_START, WORD_END, ','])
