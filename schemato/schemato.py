import urllib
import logging as log
import re
import os
import cgi

from compound_graph import CompoundGraph

import settings


class Schemato(object):
    def __init__(self, source, loglevel="ERROR"):
        """init with a local filepath or a URI"""
        super(Schemato, self).__init__()
        self.set_loglevel(loglevel)

        def _read_stream(url):
            text, url = self._get_document(url)
            return url, self._document_lines(text)
        self.url, self.doc_lines = _read_stream(source)

        self.graph = CompoundGraph(self.url)

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
        for module_path in settings.VALIDATOR_MODULES:
            path_parts = module_path.split('.')
            module = import_module(".".join(path_parts[:-1]))
            validator_fn = getattr(module, path_parts[-1])
            self.validators.add(validator_fn(self.graph, self.doc_lines, url=self.url))

    def _document_lines(self, text):
        """helper, get a list of (linetext, linenum) from a string with newlines"""
        inlines = text.split('\n')
        doc_lines = [(cgi.escape(re.sub(r'^ +| +$', '', line)), num)
                     for line, num
                     in zip(inlines, xrange(1, len(inlines) + 1))]
        return doc_lines

    def _get_document(self, url):
        """helper, open a file or url and return the content and identigier"""
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
