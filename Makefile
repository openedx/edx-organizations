all: requirements quality test

clean:
	coverage erase
	find . -name '*.pyc' -delete

quality:
	tox -e quality

requirements:
	pip install -e .    # Install this package and its dependencies
	pip install -r test-requirements.txt

test:
	tox
