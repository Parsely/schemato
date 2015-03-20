from distillery import ParselyDistiller, NewsDistiller
from schemato import Schemato
import unittest


class TestSchemato(unittest.TestCase):
    def test_schema_no_errors(self):
        scm = Schemato("test_documents/schema.html")
        results = scm.validate()
        for res in results:
            self.assertTrue(len(res) == 0)

    def test_schema_errors(self):
        scm = Schemato("test_documents/schema_errors.html")
        results = scm.validate()

        expected = {'classname': 'SchemaOrgSchemaDef',
                    'errors': [
                        {'line': '&lt;a  itemprop="copyrightNotice"',
                         'num': 63,
                         'string': 'copyrightNotice - invalid member of NewsArticle',
                         'level': 'Error'},
                        {'line': '&lt;meta itemprop="tickerSymbol" content="NYSE NYT"/&gt;',
                         'num': 74,
                         'string': 'tickerSymbol - invalid member of Organization',
                         'level': 'Error'},
                        {'line': 'itemprop="createdBy"',
                         'num': 47,
                         'string': 'createdBy - invalid member of NewsArticle',
                         'level': 'Error'},
                        {'line': '&lt;a  itemprop="usageTerms"',
                         'num': 78,
                         'string': 'usageTerms - invalid member of NewsArticle',
                         'level': 'Error'},
                        {'line': 'itemtype="http://schema.org/UserComment"',
                         'num': 111,
                         'string': 'UserComment - invalid class',
                         'level': 'Error'},
                        {'line': 'itemtype="http://schema.org/UserComment"',
                         'num': 111,
                         'string': 'UserComment - invalid class',
                         'level': 'Error'},
                        {'line': 'itemtype="http://schema.org/UserComment"',
                         'num': 111,
                         'string': 'UserComment - invalid class',
                         'level': 'Error'}
                    ],
                    'namespace': 'http://schema.org/',
                    'warnings': []}

        for res in results:
            if res.classname == 'SchemaOrgSchemaDef':
                self.assertTrue(len(res.errors) > 0)
                for err in res.errors:
                    self.assertTrue(err.string in [a['string'] for a in expected['errors']])

    def test_html_parse(self):
        text = open("test_documents/foxnews.html", "r").read()
        scm = Schemato(text, url="http://foxnews.com", loglevel="ERROR")
        results = scm.validate()
        for res in results:
            if res.classname == "ParselyPageValidator":
                self.assertTrue("ttle - invalid parsely-page field" in [a.string for a in res.errors])
                self.assertTrue(len(res.errors) == 1)

    def test_parsely_distiller(self):
        expected = {
            'author': u'Seth Fiegerman',
            'image_url': u'http://rack.0.mshcdn.com/media/ZgkyMDEyLzEyLzA0LzY4L2FwcGxlc21hbnVmLmFDeC5qcGcKcAl0aHVtYgkxMjAweDYyNyMKZQlqcGc/c3babd6d/39c/apple-s-manufacturing-partner-explains-iphone-5-supply-problems-eaf7f9f5b3.jpg',
            'link': u'http://mashable.com/2012/10/17/iphone-5-supply-problems/',
            'page_type': u'post',
            'post_id': 1432059,
            'pub_date': u'2012-10-17T11:36:40-04:00',
            'section': u'business',
            'site': 'Mashable',
            'title': u"Apple's Manufacturing Partner Explains iPhone 5 Supply Problems"
        }
        mashable = Schemato("http://mashable.com/2012/10/17/iphone-5-supply-problems/")

        d = ParselyDistiller(mashable)
        d.distill()
        self.assertEqual(d.distilled, expected)

    def test_news_distiller(self):
        expected = {
            'author': None,
            'description': 'An executive at Foxconn, Apple\'s manufacturing partner, says the iPhone 5 is "the most difficult device" it has ever had to make.',
            'id': None,
            'image_url': 'http://rack.0.mshcdn.com/media/ZgkyMDEyLzEyLzA0LzY4L2FwcGxlc21hbnVmLmFDeC5qcGcKcAl0aHVtYgkxMjAweDYyNyMKZQlqcGc/c3babd6d/39c/apple-s-manufacturing-partner-explains-iphone-5-supply-problems-eaf7f9f5b3.jpg',
            'link': 'http://mashable.com/2012/10/17/iphone-5-supply-problems/',
            'pub_date': None,
            'section': None,
            'site': 'Mashable',
            'title': "Apple's Manufacturing Partner Explains iPhone 5 Supply Problems"
        }
        mashable = Schemato("http://mashable.com/2012/10/17/iphone-5-supply-problems/")

        d = NewsDistiller(mashable)
        d.distill()
        self.assertEqual(d.distilled, expected)


if __name__ == "__main__":
    unittest.main()
