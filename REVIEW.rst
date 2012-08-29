Code Review for Schemato
========================

Project-level
-------------

Name
~~~~

We should simplify the name. Let's just use the project name "schemato".  Same
for Github name. We can refer to it as "Mr. Schemato" in the documentation to
be cute. But the project name (on PyPi, Github, in import statements) should be
simply "schemato".

OOP approach isn't quite right
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have a ``Validator`` object with a single public method, ``validate``. This
should already tell you something is wrong.

I actually do think we need an object-oriented approach here, especially since
the validator should also be caching the schema definitions similar to what the
``tldextract`` library does with TLD definitions. But right now, the ``Validator``
object is doing too much.

I think our main object should be called ``schemato.Schemato``, and we should
also expose a function called ``validate()`` which provides syntactic sugar, so
you can use the library in both a functional and object-oriented style. So, the
public API for this module is:

* ``from schemato import Schemato`` -- most flexible form
* ``from schemato import validate`` -- simple functional facade
* ``from schemato import demo`` -- simple function facade for running demo Flask web application

Our ``Schemato`` object should have one or more ``Validator`` objects
installed.  A ``Validator`` implements validation logic for a single schema,
defined by a ``SchemaDef``. So, we will have:

* ParselyPageValidator
* SchemaOrgValidator
* RNewsValidator
* OpenGraphValidator

Correspondingly:

* ParselyPageSchema
* SchemaOrgSchema
* RNewsSchema
* OpenGraphSchema

These can be organized nicely into a subpackage structure, for example:

* schemato/
    * standards/
        * rnews.py
        * schemaorg.py
        * parselypage.py
        * opengraph.py
    * web/
    * tests/

You can put the ``SchemaDef`` implementations and ``Validator`` implementations
in the same file by standard, since these are logically related.

``SchemaDef`` should handle loading and caching the standard. ``Validator``
should handle validating a page graph against the standard.

``Schemato`` should take a set of ``Validators`` and run them one by one (or,
even, in parallel!) over a page graph.

Finally, we should define a ``ValidationResult`` class which can contain the
results of a given validation, e.g. whether it was successful, and, if not
successful, what the list of errors are.

Comments and Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Another thing that should be improved is the approach to commenting. Ideally,
for the open source release, we could build all the docs using Sphinx and
publish them using ReadTheDocs.org, which is the most popular approach these
days.

This means including some ReST formatted docstrings describing modules,
classes, APIs, and possibly including a ``docs/`` subfolder with walkthrough of
how to use the library in .rst format for Sphinx.

Decouple API from server 100%
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Right now, ``mrSchemato/__init__.py`` does ``from settings import *``. We can't
have this -- the library needs to be 100% decoupled from the server
implementation with RabbitMQ, Celery, etc.

It's fine for us to provide some celery support (as an optional dependency),
e.g. ``schemato.runner.celery`` or something. You should be able to install and
use schemato though without Flask, Celery or RabbitMQ installed locally
(including the corresponding Python packages).

Avoid Copyright Notices
~~~~~~~~~~~~~~~~~~~~~~~

Copyright notices are actually meaningless and convey a false sense of
ownership. We are releasing this code to the world under an open source
license. It's fine to list your own name under an "Authors" listing, or say
that you were the primary / original author somewhere, but let's avoid
copyrights, both at the individual and company level.

Consider adding a simple CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I think it'd be great to install a binary called ``schemato`` with a simple
interface, e.g.::

    $ schemato http://arstechnica.com
    Detected Standards: open-graph, parsely-page
    open-graph Result: VALID
    parsely-page Result: VALID

    $ schemato -q http://arstechnica.com &
    [1] 22156
    $ 
    [1]+ Done       schemato -q http://arstechnica.com
    $ 

    $ schemato -v http://arstechnica.com
    Downloading schema open-graph from: http://ogp.me/.../ ... OK
    Downloading schema parsely-page from: http://parsely.com/.../ ... OK
    Detected Standards: open-graph, parsely-page
    Detected open-graph fields: [...]
    open-graph Result: VALID
    Detected parsely-page fields: [...]
    parsely-page Result: VALID
    All standards valid, exiting 0

This will also help with the prior suggestion about it being 100% decoupled
from server -- your CLI will not have the server dependency so it will ensure
that it can run without any of those settings / RabbitMQ / Celery -isms.

Tests!!
~~~~~~~

We should have at least some basic tests -- this code is very testable
ultimately, especially if we fix up the architecture a little as suggested in
this document.

We can actually re-use some of the work I did on JavaScript testing for this --
I have a sampling of crawlDB articles from Parse.ly customers, we can use these
in our test cases and make assertions. We should use standard nosetests as
expected. Also, a good idea to consider test coverage using the ``coverage.py``
module for this project.

More Standards
~~~~~~~~~~~~~~

The more I've been reading about structured metadata online, the more standards
I've found. I think it's a great idea to release it with the standards we have,
but perhaps we should specifically ask the community that implementations of
these standards would be awesome:

* hNews
* Dublin Core
* HTML4 WHAT-WG
* HTML5 semantic tags

There are definitely others outside of the pure news space that would be
interesting, so we should nudge people toward these :)

Returning the Graph?
~~~~~~~~~~~~~~~~~~~~

It occurred to me that it would be useful if the validator actually returned
the metadata graph it was able to retrieve from the page. Something like::

    {
        "metadata": {
            "title": "...",
            "author": "...",
            "section": "...",
            "pub_date": "...",
            "url": "..."
        },
        "standard": {
            "rnews": {...},
            "schemaorg": {...},
            "opengraph": {...},
            "parselypage": {...}
        }
    }

where ``metadata`` contains our "merged & normalized" view of the page metadata
that matter to us, and ``standard`` are the raw metadata attributes from each
individual metadata standard.

It also occurred to me that we could make this an API -- we should probably
make a Wufoo form to guage interest in this.

Code-Level
----------

Reliance on lepl and Flask-Celery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It turns out that celery has added official Flask support, so Flask-Celery is
officially deprecated. This is highlighted on their PyPi page:

http://pypi.python.org/pypi/Flask-Celery

Likewise, it seems like LEPL (aka lepl) is abandoned by the maintainer, who
declared it something of a failure. We seem to use a single little piece of
this library, not really sure why we pulled it in for that. 

http://www.acooke.org/lepl/discontinued.html

