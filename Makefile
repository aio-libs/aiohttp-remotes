all: test

.PHONY: format fmt
format fmt:
ifdef CI_LINT_RUN
	pre-commit run --all-files --show-diff-on-failure
else
	pre-commit run --all-files
endif


.PHONY: lint
lint: fmt
	mypy $(MYPY_DIRS)

test: lint
	pytest tests

doc:
	make -C docs html
	@echo "Open file://`pwd`/docs/_build/html/index.html"

setup init:
	pip install -r requirements/dev.txt
	pre-commit install
