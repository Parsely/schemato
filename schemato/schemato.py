import urllib
import logging as log
import re
from collections import defaultdict

import rdflib

from compound_graph import CompoundGraph
from auxparsers import ParselyPageParser

import settings


class Schemato(object):
    def __init__(self, source, loglevel="ERROR"):
        """init with a local filepath or a URI"""
        super(Schemato, self).__init__()
        self.set_loglevel(loglevel)
        text, url, doc_lines = self._read_stream(source)
        self.url = url
        self.graph = CompoundGraph(url)
        self.doc_lines = doc_lines
        self.validators = []

        def import_module(name):
            m = __import__(name)
            for n in name.split(".")[1:]:
                m = getattr(m, n)
            return m

        for module_string in settings.VALIDATOR_MODULES:
            v_package = import_module('.'.join(module_string.split('.')[:-1]))
            v_instance = getattr(v_package, module_string.split('.')[-1])(self.graph, self.doc_lines, url=self.url)
            self.validators.append(v_instance)

        # TODO - add a dublin core validator
        self.parsely_page = ParselyPageParser().parse(text, doc_lines)

    def validate(self):
        ret = defaultdict(list)

        log.debug("starting validate")
        for v in self.validators:
            if v.graph:
                ret['errors'] = []
                ret['ontology'].append(v.schema_def._ontology_file)
                log.warning("%s validation:" % (v.__class__.__name__))
                for a in v.validate():
                    ret['errors'].append(a)
                    log.warning(a)
            else:
                log.warning("no graph for %s" % v.__class__.__name__)
        ret['msg'] = "Validation complete - %s errors found" % (len(ret['errors']) if len(ret['errors']) > 0 else "no")

        log.info("returned from validate() : %s", ret)
        return ret

    def set_loglevel(self, loglevel):
        if hasattr(log, loglevel):
            log.basicConfig(level=getattr(log, loglevel))
        else:
            log.basicConfig(level=log.ERROR)
            log.error("Unrecognized loglevel %s, defaulting to ERROR", loglevel)

    def _read_stream(self, url):
        """convenience wrapper around document reading methods"""
        text, url = self._get_document(url)
        return text, url, self._document_lines(text)

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

