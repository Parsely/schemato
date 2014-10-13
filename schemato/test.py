from distillery import ParselyDistiller, NewsDistiller
from schemato import Schemato
from pprint import pprint
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
                for err in res.errors:
                    self.assertTrue(err.string in [a['string'] for a in expected['errors']])

    """
    def test_distillers(self):
        print "Loading NY Daily News..."
        nydailynews = Schemato("http://www.nydailynews.com/news/politics/obama-fights-back-2nd-debate-romney-article-1.1185271")
        print "Done."
        print "Loading Mashable..."
        mashable = Schemato("http://mashable.com/2012/10/17/iphone-5-supply-problems/")
        print "Done."

        def demo(desc, class_, site):
            print desc
            print "=" * len(desc)
            d = class_(site)
            d.distill()
            pprint({"distilled": d.distilled, "sources": d.sources})

        demo("Parse.ly strategy on Mashable", ParselyDistiller, mashable)
        demo("News strategy on Mashable", NewsDistiller, mashable)
        demo("Parse.ly strategy on NY Daily News", ParselyDistiller, nydailynews)
        demo("News strategy on NY Daily News", NewsDistiller, nydailynews)
    """


if __name__ == "__main__":
    unittest.main()
