#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from django_sample_generator.text_generator import get_text_generator


def print_help():
	sys.stdout.write("Usage: %s content_type length\n" % (sys.argv[0]))
	sys.stdout.write("Content types:\n" )
	sys.stdout.write("    w  - word\n")
	sys.stdout.write("    uw - uppercase first letter of word\n")
	sys.stdout.write("    s  - sentence\n")
	sys.stdout.write("    p  - paragraph\n")
	sys.stdout.write("    t  - text\n")


def main():
	gen = get_text_generator()

	if len(sys.argv) < 2 or len(sys.argv) > 3:
		print_help()
		sys.exit(-1)
	content_type = sys.argv[1]
	length = None
	if len(sys.argv) > 2:
		try:
			length = int(sys.argv[2])
		except ValueError:
			print_help()
			sys.exit(-1)

	if content_type == 'w':
		sys.stdout.write(gen.get_word(min_length=length or 1))
	elif content_type == 'uw':
		sys.stdout.write(gen.get_word(uppercase=True, min_length=length or 1))
	elif content_type == 's':
		sys.stdout.write(gen.get_sentence())
	elif content_type == 'p':
		sys.stdout.write(gen.get_paragraph(length))
	elif content_type == 't':
		sys.stdout.write(gen.get_text(length))
	else:
		print_help()
		sys.exit(-1)
	sys.stdout.flush()


if __name__ == "__main__":
	main()
