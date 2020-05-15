API
===

.. module:: aiohttp_remotes
.. currentmodule:: aiohttp_remotes

Setup
-----

.. cofunction:: setup(app, *tools)

   Setup tools provided by the module.

   A tool is class instance from described below list, the functon
   registers provided tools into aiohttp application *app*, e.g.::

      from aiohttp_remotes import BasicAuth, Secure, setup

      app = web.Application()

      await setup(app, Secure(), BasicAuth("user", "password", "realm"))

   Order of tools is important: in the example redirect to HTTPS is
   performed *before* credentials check, thus login/password is sent
   via SSL encrypted connection.


AllowedHosts
------------

.. class:: AllowedHosts(allowed_hosts=('*',), *, white_paths_())

   Restrict a list of host/domain names that this aiohttp application
   can serve. This is a security measure to prevent *HTTP Host header
   attacks*, which are possible even under many seemingly-safe web
   server configurations.

   :param allowed_hosts: an iterable of allowed client IP
                         addresses. ``'*'`` is a wildcard for
                         accepting any host.

   :param white_paths: an iterable of white paths, see
                       :ref:`aiohttp-remotes-white_paths` for details.

BasicAuth
---------

.. class:: BasicAuth(username, password, realm, * white_paths=())

   Protect web application by `basic auth
   <https://en.wikipedia.org/wiki/Basic_access_authentication>`_
   authorization.

   :param str username: user name

   :param str password: password

   :param str realm: realm

   :param white_paths: an iterable of white paths, see
                       :ref:`aiohttp-remotes-white_paths` for details.

CloudFlare
----------

.. class:: Cloudflare(client=None)

   Make sure that web application is protected  by CloudFlare.

   The tools should be used with :class:`XForwardedStrict` or
   :class:`XForwardedRelaxed` to setup HTTP *scheme*, *host* and *remote*
   properly.

   :param client: :class:`aiohttp.ClientSession` instance for
                  performing HTTP requests to CloudFlare configuration
                  resources.

                  The class creates a temporary client if ``None`` is
                  provided.


Forwarded
---------

.. class:: ForwardedRelaxed(num=1)

   Modify :attr:`~web.BaseRequest.scheme`,
   :attr:`~web.BaseRequest.host`, :attr:`~web.BaseRequest.remote`
   attributes giving the values from *num* ``Forwarded`` HTTP header
   record (last one by default).

   The tools is useful for getting real client IP, scheme (HTTPS or
   HTTP) and HOST if aiohttp application is deployed behind *Reverse
   Proxy* like NGINX.

   The class does not perform any security check, use it with caution.


.. class:: ForwardedStrict(trusted, *, white_paths=())

   Process ``Forwarded`` HTTP header and modify corresponding
   :attr:`~web.BaseRequest.scheme`, :attr:`~web.BaseRequest.host`,
   :attr:`~web.BaseRequest.remote` attributes in strong secure mode.

   Restrict access (return *400 Bad Request*) if *reverse proxy*
   addresses are not match provided configuration.

   :param trusted: a list of trusted reverse proxies, see
                   :ref:`aiohttp-remotes-trusted-list` for details.

   :param white_paths: an iterable of white paths, see
                       :ref:`aiohttp-remotes-white_paths` for details.


Secure
------


.. class:: Secure(*, redirect=True, redirect_url=None, white_paths=())

   Ensure that web application is handled by HTTPS
   (SSL/TLS) only, redirect plain HTTP to HTTPS automatically.

   :param bool redirect: do redirection instead of returning *400 Bad
                         Request*.

   :param redirect_url: redirection URL, the same usr as requested
                        non-secure HTTP if not specified.

   :param white_paths: an iterable of white paths, see
                       :ref:`aiohttp-remotes-white_paths` for details.

X-Forwarded
-----------

.. class:: XForwardedRelaxed(num=1)

   Modify :attr:`~web.BaseRequest.scheme`,
   :attr:`~web.BaseRequest.host`, :attr:`~web.BaseRequest.remote`
   attributes giving the values from *num* ``X-Forwarded-*`` HTTP headers
   (last record by default).

   The tools is useful for getting real client IP, scheme (HTTPS or
   HTTP) and HOST if aiohttp application is deployed behind *Reverse
   Proxy* like NGINX.

   The class does not perform any security check, use it with caution.


.. class:: XForwardedFiltered(trusted)

   The same as :class:`XForwardedRelaxed`, but rather than taking the
   values from a specific position in the ``X-Forwarded-*`` HTTP headers,
   this class takes a whiltelist of networks to treat as internal and
   finds the first external IP in the ``X-Forwarded-*`` HTTP headers.  It
   then modifies :attr:`~web.BaseRequest.scheme` and
   :attr:`~web.BaseRequest.remote` to those values.

   This class is useful when there may be an unknown number of internal
   proxies in front of a service, so there is no simple choice of *num*
   for :class:`XForwardedRelaxed`) and it isn't possible to strictly
   define the sequence of proxies for :class:`XForwardedStrict`.

   :attr:`~web.BaseRequest.host` is always set to the value of
   ``X-Forwarded-Host``, if present, since it is not generally set to a
   sequence of values separated by commas.

   If ``X-Forwarded-Proto`` contains only a single value even though
   ``X-Forwarded-For`` contains multiple values including trusted proxies,
   that single value is used for :attr:`~web.BaseRequest.scheme`.  Some
   proxies (such as the Kubernetes NGINX ingress) do not append schemes to
   ``X-Forwarded-Proto``.

   If all IPs in ``X-Forwarded-For`` are trusted, the left-most one is
   used.

   :param trusted: a set of IP addresses or networks, either IPv4 or IPv6,
                   in a form accepted by :func:`~ipaddress.ip_address` or
                   :func:`~ipaddress.ip_network`.



.. class:: XForwardedStrict(trusted, *, white_paths=())

   Process ``X-Forwarded-*`` HTTP headers and modify corresponding
   :attr:`~web.BaseRequest.scheme`, :attr:`~web.BaseRequest.host`,
   :attr:`~web.BaseRequest.remote` attributes in strong secure mode.

   Restrict access (return *400 Bad Request*) if *reverse proxy*
   addresses are not match provided configuration.

   :param trusted: a list of trusted reverse proxies, see
                   :ref:`aiohttp-remotes-trusted-list` for details.

   :param white_paths: an iterable of white paths, see
                       :ref:`aiohttp-remotes-white_paths` for details.


.. _aiohttp-remotes-trusted-list:

Trusted hosts
-------------

*trusted* parameter is a sequence of trusted hosts or networks.

The format is list of items, where every item describes a *reverse proxy*.

Item can be:

* A list of IP addresses or networks, every element is:

  * IP address is IPv4 or IPv6 in form accepted by :func:`ipaddress.ip_address`.

  * Network is IPv4 or IPv6 network in form accepted by
    :func:`ipaddress.ip_network`.

* Ellipsis ``...``

The check is performed against ``Forwarded`` or ``X-Forwarded-*`` HTTP headers.

The leftmost item in the list describes *reverse proxy* closest to web
application's host.

IP address or network is specified by strict checking, ``...`` is
the placeholder for skip checking (should be rightmost element).

In practice ellipsis is secure if used with CloudFlare
only. :class:`Cloudflare` checks corresponding proxy against a list of
CloudFlare proxy networks provided by the service at configuration
stage.


.. _aiohttp-remotes-white_paths:

White paths
-----------

Many classes from the library accepts *white_paths* parameter, an
iterable of white paths.

If :attr:`~aiohttp.web.BaseRequest.path` is in the
list all checks are skipped.

White list is useful for system routes like health checks and
monitoring.
