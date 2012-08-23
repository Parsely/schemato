from lxml import etree
from lepl.apps.rfc3696 import HttpUrl

from StringIO import StringIO
import json
import urllib
import re
from HTMLParser import HTMLParser

from errors import _error

PARSELY_PAGE_SCHEMA = "http://parsely.com/parsely_page_schema.html"

class ParselyPageValidator(object):
    def __init__(self):
        self.stdref = self.get_standard()
        self.url_validator = HttpUrl()
        return super(ParselyPageValidator, self).__init__()

    def get_standard(self):
        """get list of allowed parameters"""
        text = urllib.urlopen(PARSELY_PAGE_SCHEMA).read()
        tree = etree.parse(StringIO(text))
        stdref = tree.xpath("//div/@about")
        return [a.split(':')[1] for a in stdref]

    def _get_parselypage(self, doc_lines):
        """related to the <meta name="parsely-page"> tag, used as the default impl"""
        h_parser = HTMLParser()

        meta = [a[0] for a in doc_lines if "parsely-page" in a[0]]
        if not meta:
            return None
        meta = meta[0]

        pagemeta = [a for a in meta.split('<') if "parsely-page" in a]
        if not pagemeta:
            return None
        pagemeta = pagemeta[0]

        pagemeta = re.search('{.*?}', pagemeta).group(0)
        if not pagemeta:
            return None

        try:
            pagemeta = json.loads(pagemeta)
        except ValueError,e:
            raise ValueError("Error loading parsely-page data: %s" % e)

        for k in pagemeta.keys():
            if pagemeta[k] and type(pagemeta[k]) is not int:
                pagemeta[k] = h_parser.unescape(pagemeta[k])

        return pagemeta

    def validate(self, text, doc_lines):
        errors = []
        ret = {'ontology': [], 'ont_name': [], 'errors': []}

        try:
            self.parsely_page = self._get_parselypage(doc_lines)
        except IndexError, ValueError:
            return [_error("Failed to parse parsely-page content", doc_lines=doc_lines)]

        if self.parsely_page:
            ret['ontology'] = [PARSELY_PAGE_SCHEMA]
            ret['ont_name'] = ['parsely-page']
            for key in self.parsely_page.keys():
                err = self.check_key(key, doc_lines)
                if err:
                    errors.append(err)

        ret['errors'] = errors

        return ret

    def check_key(self, key, doc_lines):
        if key not in self.stdref:
            return _error("{0} - invalid parsely-page field", key,
                doc_lines=doc_lines)
        if key in ["link", "image_url"]:
            if not self.url_validator(self.parsely_page[key]):
                return _error("{0} - invalid url for field '{1}'", self.parsely_page[key], key,
                    doc_lines=doc_lines)
        return None
