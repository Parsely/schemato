schemato
========

Meet Mr. Schemato, the friendly semantic web validator and distiller that is
making metadata cool again.

Validator
---------

This is a validator for the a number of embedded metadata standards. It
works by reading the object ontology and comparing each of a set of
parsed tuples from a document against this ontology.

To test the validation, clone this repo, pip install the requirements, and run

    >>> from schemato import Validator
    >>> validator = Validator()
    >>> validator.validate("test_documents/rdf.html")

this will run a validation on a correctly-implemented RDFa document (rdf.html). To run
a validation on a document with errors, use one of the error test files

``>>> Schemato("test_documents/schema_errors.html").validate()``

The full schema.org standard is now also supported. You can validate any page
that uses this standard against the RDFa ontology hosted at schema.org. To
test this, you can find an arbitrary nytimes.com article, or copy and paste
this example

``>>> Schemato("http://www.nytimes.com/2012/07/19/world/middleeast/.....html").validate()``

The ``test_documents`` directory also includes four documents for testing the validation in RDFa
and microdata, both with and without errors built in. Running the validator on
either of the correct files should yield no errors.

Distiller
---------

Schemato's distiller framework lets you implement strategies for creating a "normalized" set of metadata by mixing and matching metadata from different supported standards.

Supported so far: 

    * parsely-page
    * OpenGraph
    * Schema.org NewsArticle

Take a look at the clean Python class definitions that describe the strategies:

https://github.com/Parsely/schemato/blob/master/schemato/distillery.py

There are two examples -- one that tries pp and falls back on
Schema.org/OpenGraph (called ``ParselyDistiller``) and another the tries Schema.org
and falls back on OpenGraph (called ``NewsDistiller``).

The distiller returns a clean Python dictionary that has all the extracted
fields, as well as a dictionary describing which metadata standard was used to
source each field. The framework is defined here:

https://github.com/Parsely/schemato/blob/master/schemato/distillers.py

Here is an example of usage:

    >>> from schemato import Schemato
    >>> from distillery import ParselyDistiller, NewsDistiller
    >>> mashable = Schemato("http://mashable.com/2012/10/17/iphone-5-supply-problems/")
    >>> ParselyDistiller(mashable).distill()
    {'author': u'Seth Fiegerman',
    'image_url': u'http://5.mshcdn.com/wp-content/uploads/2012/10/iphone-lineup.jpg',
    'link': u'http://mashable.com/2012/10/17/iphone-5-supply-problems/',
    'page_type': u'post',
    'post_id': u'1432059',
    'pub_date': u'2012-10-17T11:36:40+00:00',
    'section': u'bus',
    'site': 'Mashable',
    'title': u"Apple's Manufacturing Partner Explains iPhone 5 Supply Problems"}

In this case, Mashable implements the parsely-page metadata field, which is
used to source all the defined properties for this distiller.

    >>> d = NewsDistiller(mashable)
    >>> d.distill()
    {'author': None,
    'id': None,
    'image_url': 'http://5.mshcdn.com/wp-content/uploads/2012/10/iphone-lineup.jpg',
    'link': 'http://mashable.com/2012/10/17/iphone-5-supply-problems/',
    'pub_date': None,
    'section': None,
    'title': "Apple's Manufacturing Partner Explains iPhone 5 Supply Problems"}
    >>> d.sources
    {'author': None,
    'id': None,
    'image_url': 'og:image',
    'link': 'og:url',
    'pub_date': None,
    'section': None,
    'title': 'og:title'}

In this case, our strategy did not involve parsely-page, and instead used
Schema.org and OpenGraph. Since Mashable does not implement Schema.org but does
implement OpenGraph, it comes up with the fields it can. The ``sources`` property 
shows which fields were populated and how they got their values.

Hosted Service
--------------

The schemato module is also incorporated into a web service that provides
a nice frontend for the validation. To test this service locally, run
``python schemato_web.py``. Then navigate to localhost:5000, paste
a url into the search bar, and click "Validate" to run a validation on the document.

Running this service locally also requires celery and rabbitmq to be running
and properly configured. RabbitMQ and celery can be configured to work
together using the supplied example.schemato\_config.py file. Change its name
to schemato\_config.py and replace the dummy username, password, and vhost
fields to the appropriate RabbitMQ settings for your system.

Requirements
------------

Simply use ``pip install -r requirements.txt`` to install the dependencies for
this project. It also requires a local RabbitMQ server, which can be
downloaded at http://www.rabbitmq.com/download.html

Authors
-------

schemato was designed and implemented by Emmett Butler, Parse.ly, Inc.

parts were contributed by Andrew Montalenti, Parse.ly
