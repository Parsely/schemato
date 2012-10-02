import urllib
import re
from collections import defaultdict
import sys

#from parsely_page import ParselyPageValidator
from errors import _error
from graph import Graph
from settings import *


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

        # attempt to read the file or url. if it fails, exit with error
        try:
            text, url = self._read_stream(stream)
        except IOError, e:
            ret['msg'] = e.message
            return dict(ret)

        # place the url into the returned data structure to surface to frontend
        ret['url'].append(stream)

        # perform parsely-page validation
        ppage = self.ppage.validate(text, self.doc_lines)
        # if the validation returns a result, include this result in the main
        # return value
        if ppage['ont_name']:
            for a in ppage['ontology']:
                ret['ontology'].append(a)
            for a in ppage['ont_name']:
                ret['ont_name'].append(a)
            for a in ppage['errors']:
                ret['errors'].append(a)

        # now do the rest of the validation
        # make a list of Graphs
        # handle errors in the case where that list is empty
        self.graphs = self._graphs_from_source(stream)
        if not self.graphs:
            ret['msg'] = "No recognized namespaces found"
            # turns out this is actually not an "error", should raise more of a "warning"
            prefixes = self.search_prefixes(text)
            if prefixes:
                ret['msg'] += " - did you forget to include a namespace for one of these prefixes : %s ?" % ", ".join(["'%s'" % a for a in prefixes])
            return dict(ret)

        # now that we have a list of graphs representing the different standards on
        # the page, check them all
        for graph in self.graphs:
            for ns in graph.ns_ont.keys():
                # include the ontology name and link in the returned result
                ret['ontology'].append(graph.ns_ont[ns])
                ret['ont_name'].append(ns)
            err = graph.check(self.doc_lines)
            if err:
                # for some reason we copy each element sequentially instead of just
                # copying the list?
                for e in err:
                    ret['errors'].append(e)

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

        # this function is also called in validate(), that's dumb
        text, url = self._read_stream(url)

        # check if there are any known standards in the document
        # this has to be better, since checking for the presence of the
        # schema url isn't really enough
        namespaces = [a for a in RDFA_NAMESPACES+MICRODATA_NAMESPACES if a in text]
        if not namespaces:
            return None

        # make sure both of the opengraph links are in this list, i guess?
        # this is convoluted
        if OG_ROOT in namespaces:
            namespaces.append(OG_ALT_ROOT)
        if OG_ALT_ROOT in namespaces:
            namespaces.append(OG_ROOT)
        # build the graphs
        graphs = self._graphs_from_namespaces(url, namespaces)

        # looks like this could just as easily happen as "if not namespaces"
        if not graphs:
            raise ValueError('No supported namespace found.\nSupported namespaces: %s' % self.namespaces)

        return graphs

    def _graphs_from_namespaces(self, url, namespaces):
        """take some namespaces and a locator, return the Graphs
        based thereon"""
        rdf_graph, microdata_graph = None, None
        ret = []

        for ns in namespaces:
            # make one big graph for the rdf standards
            if ns in RDFA_NAMESPACES:
                rdf_graph = Graph(url, 'rdfa')
                # oh also, this assignment happens IN ANOTHER CLASS
                # wow cool coupling bro
                rdf_graph.ns_ont[ns] = ns2ont[ns]
            # make another single graph for the microdata ones
            elif ns in MICRODATA_NAMESPACES:
                microdata_graph = Graph(url, 'microdata')
                microdata_graph.ns_ont[ns] = ns2ont[ns]

        # this is awful. I forget why I actually wrote it this way, so here's what
        # i now *think* is happening here
        # Graph() constructor sets a bunch of values in the object
        # this function sets ns_ont[ns] in the object, which is a dict of
        # namespace:namespace_link
        # why this doesn't get set in the object itself is currently beyond me
        # probably some misguided attempt at DRY
        # once this has been done, build_graph can be called
        # since it depends on ns_ont being set
        # this is the most disturbing example of coupling between two
        # supposedly encapsulated classes I've ever written
        # because build_graph is state sensitive and can only work after
        # setting ns_ont! NOOOOOOOOOOOOOOOOoooooooo........ *falls into pit*
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
        # this is so dumb, it increases coupling and makes maintenance harder
        # don't set a class property in what is *supposed* to be a helper method
        # ya bimbo
        self.doc_lines = self._document_lines(text)
        return text, url

