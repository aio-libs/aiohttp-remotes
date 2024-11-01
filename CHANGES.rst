.. towncrier release notes start

1.3.0 (2024-11-01)
==================

* Added explicit tests for running with Python 3.11, 3.12, 3.13

Bugfixes
--------

- Fix for ``X-Forwarded-Host`` parsing when it contains multiple hosts. (`#436 <https://github.com/aio-libs/aiohttp-remotes/issues/436>`_)

Deprecations and Removals
-------------------------

- Dropped Python 3.7 and 3.8 support, the minimal supported aiohttp is 3.9

1.2.0 (2021-12-15)
==================

* Raise a ``HTTPBadRequest`` instead of ``ValueError`` when ``X-Forwarded-For`` header is not a valid IP. (`#311 <https://github.com/aio-libs/aiohttp-remotes/issues/311>`_)

* Dropped Python 3.6 support, the minimal supported aiohttp is 3.8.1 (`#331 <https://github.com/aio-libs/aiohttp-remotes/issues/331>`_)


1.1.0 (2021-11-04)
==================

* Added support for Python 3.10

1.0.0 (2020-11-05)
==================

* Drop Python 3.5 support

* Officially support Python 3.8 and Python 3.9

* Provide ``X-Forwarded`` middleware that filters out trusted values (#153)

* Add type annotations

0.1.2 (2018-03-01)
==================

* Correctly process IPv6 peer names (#18)

0.1.1 (2017-12-29)
==================

* Small doc fixes


0.1.0 (2017-12-19)
==================

* First public release
