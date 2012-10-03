import urllib
import logging as log
import re

from schemas.rnews import RNewsValidator
from schemas.opengraph import OpenGraphValidator
from schemas.schemaorg import SchemaOrgValidator
from compound_graph import CompoundGraph

import rdflib

log.basicConfig(level=log.INFO)

class Schemato(object):
    def __init__(self, source):
        super(Schemato, self).__init__()
        text, url, doc_lines = self._read_stream(source)
        self.url = url
        self.graph = CompoundGraph(url)
        self.doc_lines = doc_lines
        log.debug("in schemato init: %s" % self.graph.rdfa_graph)
        # populate from a file somehow
        self.validators = []
        self.validators.append(RNewsValidator(self.graph, self.doc_lines))
        self.validators.append(OpenGraphValidator(self.graph, self.doc_lines, self.url))
        self.validators.append(SchemaOrgValidator(self.graph, self.doc_lines))

    def validate(self):
        log.debug("starting validate")
        for v in self.validators:
            if v.graph:
                log.info(v.validate())
            else:
                log.info("no graph for %s" % v.__class__.__name__)

    def _document_lines(self, text):
        """helper, get a list of (linetext, linenum) from a string with newlines"""
        doc_lines, num = [], 0
        for line in text.split('\n'):
            num += 1
            line = re.sub(r'^ +| +$', '', line)
            line = line.replace("<", "&lt;").replace(">", "&gt;")
            doc_lines.append((line, num))
        return doc_lines

    def _get_document(self, url):
        """helper, open a file or url and return the doctype and content separately"""
        try:
            if "http://" not in url:
                scheme_url = "http://%s" % url
            else:
                scheme_url = url
            try:
                text = urllib.urlopen(scheme_url).read()
                url = scheme_url
            except:
                text = open(url, "r").read()
        except:
            raise IOError('Failed to read stream from %s' % url)

        return (text, url)

    def _read_stream(self, url):
        text, url = self._get_document(url)
        return text, url, self._document_lines(text)
