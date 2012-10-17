from StringIO import StringIO
import json
import urllib
import re
from HTMLParser import HTMLParser

from errors import _error

class ParselyPageParser(object):
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

    def parse(self, text, doc_lines):
        try:
            self.parsely_page = self._get_parselypage(doc_lines)
            return self.parsely_page
        except IndexError, ValueError:
            return None
