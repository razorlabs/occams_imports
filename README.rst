OCCAMS Imports
==============

Application for data mapping and import from other databases


Rationale
---------

On some occasions, data teams will want to import external data sets into
OCCAMS. This tool will facilitate the pipelines necessary to continuously
integrate external data into a "master" OCCAMS installation.


Goals
-----

Some goals of this product:

  * PID translation
  * External codebook parsing
  * Schema mapping
  * External data upload


System Requirements
-------------------

  * Python 2.7+
  * npm
    - lessc (must be installed globally, i.e. with "-g" option)
  * redis
  * PostgreSQL 9.3+


Authentication
++++++++++++++

Because many organizations have their politics of authentication, this app
tries to not force any authentication paradigm on the client and instead
uses `repoze.who` to allow clients to supply their own authentication via
customized-organization-specific plugins.


Installation
------------

Add as an occams plugin via::

  occams.apps = occams_imports

