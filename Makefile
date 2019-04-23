all: requirements quality test

clean:
	coverage erase
	find . -name '*.pyc' -delete

quality:
	tox -e quality

requirements:
	pip install -e .    # Install this package and its dependencies
	pip install -r test-requirements.txt

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the requirements text files based on the requirements/*.in files
	pip install -q pip-tools
	pip-compile --upgrade -o test-requirements.txt requirements/test.in
	# Let tox control the Django version for tests
	sed -i.tmp '/^djangorestframework==/d' test-requirements.txt
	rm test-requirements.txt.tmp

test:
	tox
