=====================
Sample data generator
=====================

Install
-------

`pip install https://github.com/mireq/django-sample-data-generator.git`

Usage
-----

Settings
^^^^^^^^

.. code:: python

	INSTALLED_APPS = (
		# ...
		'django_sample_generator',
	)

	SAMPLE_DATA_GENERATORS = (
		'blog.generators.register',
	)

Example
^^^^^^^

.. code:: python

	# blog/generators.py

	from django_sample_generator import GeneratorRegister, ModelGenerator, NameSample, TextSample
	from .models import Blog

	class BlogGenerator(ModelGenerator):
		title = NameSample()
		content = TextSample(text_type=TextSample.Paragraph)

	register = GeneratorRegister()
	register.register(BlogGenerator(Blog, 1000))

.. code:: bash

	python manage.py create_sample_data
