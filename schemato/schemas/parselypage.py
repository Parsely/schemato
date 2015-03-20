import json

from lxml import etree
from lepl.apps.rfc3696 import HttpUrl
from six import StringIO, iteritems
from six.moves.urllib.request import urlopen
from six.moves.html_parser import HTMLParser, HTMLParseError

from ..errors import _error
from ..validationresult import ValidationResult, ValidationWarning
from ..validator import SchemaValidator


PARSELY_PAGE_SCHEMA = "http://parsely.com/static/data/parsely_page_schema.html"


class ParselyPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.ppage = None

    def handle_starttag(self, tag, attrs):
        if self.ppage is not None or tag != "meta":
            return

        attrs = dict(attrs)
        if attrs.get("name") == "parsely-page":
            ppage = attrs.get("content", attrs.get("value"))
            if ppage:
                try:
                    self.ppage = json.loads(ppage)
                except:
                    raise HTMLParseError("bad ppage")  # bad ppage

    def original_unescape(self, s):
        """Since we need to use this sometimes"""
        if isinstance(s, basestring):
            return unicode(HTMLParser.unescape(self, s))
        elif isinstance(s, list):
            return [unicode(HTMLParser.unescape(self, item)) for item in s]
        else:
            return s

    def unescape(self, s):
        return s


class ParselyPageValidator(SchemaValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(ParselyPageValidator, self).__init__(graph, doc_lines, url=url)
        self.text = '\n'.join([a[0] for a in doc_lines])
        self.stdref = self.get_standard()
        self.url_validator = HttpUrl()
        self.data = self._get_parselypage(self.text)

    def get_standard(self):
        """get list of allowed parameters"""
        try:
            res = urlopen(PARSELY_PAGE_SCHEMA)
        except:
            return []
        text = res.read()
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        tree = etree.parse(StringIO(text))
        stdref = tree.xpath("//div/@about")
        return [a.split(':')[1] for a in stdref]

    def _get_parselypage(self, body):
        """extract the parsely-page meta content from a page"""
        parser = ParselyPageParser()
        ret = None
        try:
            parser.feed(body)
        except HTMLParseError:
            pass  # ignore and hope we got ppage
        if parser.ppage is None:
            return

        ret = parser.ppage
        if ret:
            ret = {parser.original_unescape(k): parser.original_unescape(v)
                   for k, v in iteritems(ret)}
        return ret

    def validate(self):
        result = ValidationResult("parsely-page", self.__class__.__name__)

        if self.data:
            for key in self.data:
                res = self.check_key(key)
                if res:
                    result.add_error(res)

        return result

    def check_key(self, key):
        if key not in self.stdref:
            err = _error("{0} - invalid parsely-page field", key,
                         doc_lines=self.doc_lines)
            return ValidationWarning(
                ValidationResult.ERROR, err['err'], err['line'], err['num'])
        if key in ["link", "image_url"]:
            if not self.url_validator(self.data[key]):
                err = _error(
                    "{0} - invalid url for field '{1}'", self.data[key], key,
                    doc_lines=self.doc_lines)
                return ValidationWarning(
                    ValidationResult.ERROR, err['err'], err['line'],
                    err['num'])
        return None
