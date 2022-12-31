=====================
Sample data generator
=====================

|codecov| |version| |downloads| |license|

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

.. |codecov| image:: https://codecov.io/gh/mireq/django-sample-data-generator/branch/master/graph/badge.svg?token=1IMD01ean6
	:target: https://codecov.io/gh/mireq/django-sample-data-generator

.. |version| image:: https://badge.fury.io/py/django-sample-data-generator.svg
	:target: https://pypi.python.org/pypi/django-sample-data-generator/

.. |downloads| image:: https://img.shields.io/pypi/dw/django-sample-data-generator.svg
	:target: https://pypi.python.org/pypi/django-sample-data-generator/

.. |license| image:: https://img.shields.io/pypi/l/django-sample-data-generator.svg
	:target: https://pypi.python.org/pypi/django-sample-data-generator/
