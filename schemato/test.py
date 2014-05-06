from distillery import ParselyDistiller, NewsDistiller
from schemato import Schemato
from pprint import pprint
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
