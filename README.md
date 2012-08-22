schema.org/rNews Validator
==========================

This is a validator for the a number of embedded metadata standards. It
works by reading the object ontology and comparing each of a set of
parsed tuples from a document against this ontology.

To test the validation, clone this repo and run

    >>> from mrSchemato import Validator
    >>> validator = Validator()
    >>> validator.validate("docs/rdf.html")

this will run a validation on a correctly-implemented RDFa document (rdf.html). To run
a validation on a document with errors, use one of the error test files

``>>> validator.validate("docs/schema_errors.html")``

The full schema.org standard is now also supported. You can validate any page
that uses this standard against the RDFa ontology hosted at schema.org. To
test this, you can find an arbitrary nytimes.com article, or copy and paste
this example

``>>> validator.validate("http://www.nytimes.com/2012/07/19/world/middleeast/.....html")``

The ``docs`` directory also includes four documents for testing the validation in RDFa
and microdata, both with and without errors built in. Running the validator on
either of the correct files should yield no errors.

Hosted Service
--------------

The mrSchemato module is also incorporated into a web service that provides
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
