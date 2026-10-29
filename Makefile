all: requirements quality test

.PHONY: clean requirements quality test upgrade

clean:
	coverage erase
	find . -name '*.pyc' -delete

quality:
	pycodestyle src/organizations
	pylint --rcfile=pylintrc src/organizations

requirements:
	uv sync --locked --group dev

upgrade: ## update python dependencies
	uv run --with edx-lint edx_lint write_uv_constraints pyproject.toml
	uv lock --upgrade

test:
	python -Wd -m pytest $(PYTEST_ARGS)
	coverage report
