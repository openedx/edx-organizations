all: requirements quality test

.PHONY: clean requirements quality test upgrade

clean:
	coverage erase
	find . -name '*.pyc' -delete

quality:
	tox -e quality

requirements:
	pip install -qr requirements/pip-tools.txt
	pip install -e .    # Install this package and its dependencies
	pip install -r test-requirements.txt


COMMON_CONSTRAINTS_TXT=requirements/common_constraints.txt
.PHONY: $(COMMON_CONSTRAINTS_TXT)
$(COMMON_CONSTRAINTS_TXT):
	wget -O "$(@)" https://raw.githubusercontent.com/edx/edx-lint/master/edx_lint/files/common_constraints.txt || touch "$(@)"

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: $(COMMON_CONSTRAINTS_TXT)
	## update the requirements text files based on the requirements/*.in files
	pip install -qr requirements/pip-tools.txt
	pip-compile --upgrade --allow-unsafe -o requirements/pip-tools.txt requirements/pip-tools.in
	pip install -qr requirements/pip-tools.txt
	pip-compile --upgrade --allow-unsafe -o requirements/base.txt requirements/base.in
	pip-compile --upgrade -o test-requirements.txt requirements/test.in
	# Let tox control the Django version for tests
	sed -i.tmp '/^django==/d' test-requirements.txt
	rm test-requirements.txt.tmp

test:
	tox
