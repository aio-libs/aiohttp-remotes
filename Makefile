isort:
	isort -rc aiohttp_remotes tests

flake:
	flake8 aiohttp_remotes tests
	isort -c -rc aiohttp_remotes tests

test: flake
	pytest tests
