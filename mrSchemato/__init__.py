import urllib
import re
from collections import defaultdict
import sys

from parsely_page import ParselyPageValidator
from errors import _error
from graph import Graph
from settings import *


def prettyprint(dict_2d):
    for k in dict_2d:
        print k
        for g in dict_2d[k]:
            print "   %s" % str(g)
        print


class Validator(object):
    def __init__(self):
        self.namespaces = [RNEWS_ROOT, SCHEMA_ROOT, OG_ROOT, OG_ALT_ROOT]
        self.ppage = ParselyPageValidator()
        super(Validator, self).__init__()

    ##################################################################
    #                           FRONTENDS                            #
    ##################################################################
    def validate(self, stream):
        """frontend, returns a list of errors"""
        errors = []
        ret = defaultdict(list)

        try:
            text, url = self._read_stream(stream)
        except IOError, e:
            ret['msg'] = e.message
            return dict(ret)

        ret['url'].append(stream)

        ppage = self.ppage.validate(text, self.doc_lines)
        if ppage:
            ret['errors'].append(ppage)

        self.graphs = self._graphs_from_source(stream)
        if not self.graphs:
            ret['msg'] = "No recognized namespaces found"
            prefixes = self.search_prefixes(text)
            if prefixes:
                ret['msg'] += " - did you forget to include a namespace for one of these prefixes : %s ?" % ", ".join(["'%s'" % a for a in prefixes])
            return dict(ret)

        for graph in self.graphs:
            for ns in graph.ns_ont.keys():
                ret['ontology'].append(graph.ns_ont[ns])
                ret['ont_name'].append(ns)
            ret['errors'].append(graph.check(self.doc_lines))

        ret['errors'] = sum(ret['errors'], [])
        ret['msg'] = "Validation complete - %s errors found" % (len(ret['errors']) if len(ret['errors']) > 0 else "no")
        return dict(ret)

    ######################################################################
    #                            WRAPPERS                                #
    ######################################################################
    def _graphs_from_source(self, url):
        """wrapper for _graphs_from_namespaces, builds a list of namespaces
        used in the document"""
        # make sure these are not still set from a previous run
        graphs = []

        text, url = self._read_stream(url)

        namespaces = [a for a in RDFA_NAMESPACES+MICRODATA_NAMESPACES if a in text]
        if not namespaces:
            return None

        if OG_ROOT in namespaces:
            namespaces.append(OG_ALT_ROOT)
        if OG_ALT_ROOT in namespaces:
            namespaces.append(OG_ROOT)
        graphs = self._graphs_from_namespaces(url, namespaces)

        if not graphs:
            raise ValueError('No supported namespace found.\nSupported namespaces: %s' % self.namespaces)

        return graphs

    def _graphs_from_namespaces(self, url, namespaces):
        """parse a stream (either a web document or a local file)
        into graphs based on rdf and/or microdata"""
        rdf_graph, microdata_graph = None, None
        ret = []

        for ns in namespaces:
            if ns in RDFA_NAMESPACES:
                rdf_graph = Graph(url, 'rdfa')
                rdf_graph.ns_ont[ns] = ns2ont[ns]
            elif ns in MICRODATA_NAMESPACES:
                microdata_graph = Graph(url, 'microdata')
                microdata_graph.ns_ont[ns] = ns2ont[ns]

        if rdf_graph:
            rdf_graph.build_graph()
            ret.append(rdf_graph)
        if microdata_graph:
            microdata_graph.build_graph()
            ret.append(microdata_graph)

        return ret

    #################################################################
    #                          HELPERS                              #
    #################################################################
    def _document_lines(self, text):
        """helper, get a list of (linetext, linenum) from a string with newlines"""
        doc_lines, num = [], 0
        for line in text.split('\n'):
            num += 1
            line = re.sub(r'^ +| +$', '', line)
            line = line.replace("<", "&lt;").replace(">", "&gt;")
            doc_lines.append((line, num))
        return doc_lines

    def search_prefixes(self, text):
        print COMMON_PREFIXES
        print text
        print "og: in text: %s" % ('og:' in text)
        return [a for a in COMMON_PREFIXES if a in text]

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

        doctype = re.search(r'<!DOCTYPE.*?>', text)
        if doctype:
            doctype = doctype.group(0)

        return (doctype, text, url)

    def _read_stream(self, url):
        """wrapper, given a url returns the text read from that url
        also sets self.doc_lines as an array of tuples of the form
        (line number, line text) containing all lines of the read text"""
        doctype, text, url = self._get_document(url)
        self.doc_lines = self._document_lines(text)
        return text, url

