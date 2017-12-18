.. aiohttp-remotes documentation master file, created by
   sphinx-quickstart on Mon Dec  4 15:10:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aiohttp-remotes's documentation!
===========================================

.. currentmodule:: aiohttp_remotes

The library is a set of useful tools for :mod:`aiohttp.web` server.

The full list of tools is:

* :class:`AllowedHosts` -- restrict a set of incoming connections to
  allowed hosts only.
* :class:`BasicAuth` -- protect web application by *basic auth*
  authorization.
* :class:`Cloudflare` -- make sure that web application is protected
  by CloudFlare.
* :class:`ForwardedRelaxed` and :class:`ForwardedStrict` -- process
  ``Forwarded`` HTTP header and modify corresponding
  :attr:`~web.BaseRequest.scheme`, :attr:`~web.BaseRequest.host`,
  :attr:`~web.BaseRequest.remote` attributes in strong secured and
  relaxed modes.
* :class:`Secure` -- ensure that web application is handled by HTTPS
  (SSL/TLS) only, redirect plain HTTP to HTTPS automatically.
* :class:`XForwardedRelaxed` and :class:`XForwardedStrict` -- the same
  as ``ForwardedRelaxed`` and ``ForwardedStrict`` but process old-fashion
  ``X-Forwarded-*`` headers instead of new standard ``Forwarded``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
