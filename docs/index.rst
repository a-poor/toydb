
ToyDB
======

Welcome to ToyDB's documentation!
----------------------------------

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   modules

About
=====

.. image:: https://img.shields.io/pypi/v/toydb
  :target: https://pypi.org/project/toydb
  :alt: PyPI
.. image:: https://github.com/a-poor/toydb/workflows/Python%20package/badge.svg
  :target: https://github.com/a-poor/toydb/actions
  :alt: GitHub Action Build Status
.. image:: https://img.shields.io/pypi/pyversions/toydb
  :target: https://pypi.org/project/toydb
  :alt: PyPI - Python Version
.. image:: https://img.shields.io/github/license/a-poor/toydb
  :target: https://github.com/a-poor/toydb/blob/main/LICENSE
  :alt: GitHub Project License
.. image:: https://readthedocs.org/projects/toydb/badge/?version=latest
  :target: https://toydb.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status


*created by Austin Poor*

A small, toy database written in pure python.

* GitHub: https://github.com/a-poor/toydb
* PyPi Package: https://pypi.org/project/toydb
* Read the Docs: https://toydb.readthedocs.io

I started writing ``ToyDB`` as a *toy* project, in order to get a better sense of how RDBMSs work.

My goal isn't to write a high-performance database or a fully ANSI compliant RDBMS, it's to continue to get a better understanding of the inner workings of a database.

Installation
-------------

``ToyDB`` can be installed using PyPi:

.. code-block:: console

    $ pip install toydb

Status
-------

**NOTE: Still in development.**

* Add indexes and keys
* Implement ``ORDER BY``

There currently isn't any functionality for ``JOIN``s or ``GROUP BY``s.

Feedback
----------

I'd love to hear your thoughts or suggestions on ``ToyDB``.

Please feel free to reach out to me here or on `twitter <https://twitter.com/austin_poor>`_!
