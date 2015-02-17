import urllib
import logging
import re

from pkg_resources import iter_entry_points
from StringIO import StringIO

from .compound_graph import CompoundGraph
from .schemas.parselypage import ParselyPageValidator


log = logging.getLogger(__name__)


class Schemato(object):
    def __init__(self, source, url=None, loglevel="ERROR"):
        """init with a local filepath or a URI"""
        super(Schemato, self).__init__()
        self.set_loglevel(loglevel)

        graph_source = source
        if url is not None:
            graph_source = StringIO(source)

        self.graph = CompoundGraph(graph_source)

        def _read_stream(source):
            text, url = self._get_document(source)
            return url, self._document_lines(text)

        parsed_url, self.doc_lines = _read_stream(source)
        self.url = url
        if url is None:
            self.url = parsed_url

        validator = ParselyPageValidator(self.graph, self.doc_lines)
        self.parsely_page = validator.data

    def validate(self):
        self._load_validators()

        results = [v.validate() for v in self.validators]
        log.info("returned from validate() : %s", results)
        for res in results:
            log.info(res.to_json())
        return results

    def set_loglevel(self, loglevel):
        if hasattr(log, loglevel):
            log.basicConfig(level=getattr(log, loglevel))
        else:
            log.basicConfig(level=log.ERROR)
            log.error(
                "Unrecognized loglevel %s, defaulting to ERROR", loglevel)

    def _load_validators(self):
        for entry_point in iter_entry_points('schemato_validators'):
            validator_fn = entry_point.load()
            validator = validator_fn(self.graph, self.doc_lines, url=self.url)
            self.validators.add(validator)

    def _document_lines(self, text):
        """helper, get a list of (linetext, linenum) from a string with
        newlines
        """
        inlines = text.split('\n')
        doc_lines = [(re.sub(r'^ +| +$', '', line), num)
                     for line, num
                     in zip(inlines, xrange(1, len(inlines) + 1))]
        return doc_lines

    def _get_document(self, source):
        """helper, open a file or url and return the content and identifier"""
        scheme_url = source
        if not source.startswith("http"):
            scheme_url = "http://%s" % source

        text = source

        try:
            text = urllib.urlopen(scheme_url).read()
        except:
            pass
        else:
            return (text, scheme_url)

        try:
            text = open(source, "r").read()
        except:
            pass
        else:
            return (text, source)

        return (text, None)
