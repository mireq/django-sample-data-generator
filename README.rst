=====================
Sample data generator
=====================

Install
-------

.. code:: bash

	pip install django-sample-data-generator


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
		'blog.generators',
	)

Example
^^^^^^^

.. code:: python

	# blog/generators.py

	from django_sample_generator import generator
	from .models import Blog

	class BlogGenerator(generator.ModelGenerator):
		class Meta:
			model = Blog

	generators = [
		BlogGenerator(10), # 10 blogs
	]

.. code:: bash

	python manage.py create_sample_data
