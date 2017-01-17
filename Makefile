clean:
	coverage erase
	find . -name '*.pyc' -delete

quality:
	pep8 --config=.pep8 organizations
	pylint --rcfile=pylintrc organizations

requirements:
	pip install -e .    # Install this package and its dependencies
	pip install -r test-requirements.txt

test:
	django-admin.py test organizations --settings=test_settings --with-coverage --cover-package=organizations
	coverage report

.PHONY: clean, quality, requirements, test
