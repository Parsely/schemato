schemato
========

Validator
---------

This is a validator for HTML-embedded metadata standards. It knows the
location of the official schema definitions, and uses these documents as
validation templates. As a contributor, you can easily subclass the base
validator class to plug into this functionality.

To see the validator in action:

    $ pip install schemato
    $ ipython
    >>> from schemato import Schemato
    >>> sc = Schemato("../test_documents/rdf.html", loglevel="INFO")
    >>> sc.validate()

The first time you run schemato, it will make requests for the latest versions
of the official schema definitions. These files are cached locally with
a fairly long expiry, to avoid the overhead of web requests. Schemato will
then call the ``validate()`` method of the Validator subclasses listed in
settings.py.

There are a few other test documents available for validation in the
test\_documents subdirectory.

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
