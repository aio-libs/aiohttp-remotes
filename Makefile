all: test

isort:
	isort -rc aiohttp_remotes tests

flake:
	flake8 aiohttp_remotes tests
	isort -c -rc aiohttp_remotes tests

test: flake
	pytest tests

doc:
	make -C docs html
	@echo "Open file://`pwd`/docs/_build/html/index.html"
