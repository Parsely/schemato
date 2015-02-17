import urllib
import logging as log
import re
import os

from compound_graph import CompoundGraph
from StringIO import StringIO

from .schemas.parselypage import ParselyPageValidator
from .settings import VALIDATOR_MODULES


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

        self.parsely_page = ParselyPageValidator(self.graph, self.doc_lines).data

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
            log.error("Unrecognized loglevel %s, defaulting to ERROR", loglevel)

    def _load_validators(self):
        def import_module(name):
            m = __import__(name)
            for n in name.split(".")[1:]:
                m = getattr(m, n)
            return m
        # include the parent directory in the path, to allow relative imports of
        # modules from settings
        os.sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        self.validators = set()
        for module_path in VALIDATOR_MODULES:
            path_parts = module_path.split('.')
            module = import_module(".".join(path_parts[:-1]))
            validator_fn = getattr(module, path_parts[-1])
            validator = validator_fn(self.graph, self.doc_lines, url=self.url)
            self.validators.add(validator)

    def _document_lines(self, text):
        """helper, get a list of (linetext, linenum) from a string with newlines"""
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
