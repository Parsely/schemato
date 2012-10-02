import rdflib.term as rt
from pyMicrodata import pyMicrodata
from pyRdfa import pyRdfa
import rdflib
import os

from collections import defaultdict

from schemato.utils import deepest_node


# what functionality is common to every single schema def?
class SchemaDef(object):
    """class to handle the loading and caching of a standard
    ASSUMPTIONS:
        This class holds the definition of a standard
        It does not perform any validation against that standard
        This class knows nothing about the input file being validated
    """
    def __init__(self):
        super(SchemaDef, self).__init__()
        self._ontology_file = ""
        self.ontology = defaultdict(list)
        self.attributes_by_class = defaultdict(list)
        self._ontology_parser_function = None
        self.lexicon = {}

    def _pull_standard(self):
        # if it has been > x days since last cache
        #   request the latest version of self._ontology_file
        #   self._cache_standard(pulled_file)
        # return file object
        return self._ontology_file

    def _cache_standard(self, stdfile):
        """the point of caching is to avoid extraneous web requests"""
        # if the cache is empty or if stdfile is different
        # from cached version, cache stdfile
        pass

    def _schema_nodes(self):
        """parse the ontology file into a graph"""

        name, ext = os.path.splitext(self._ontology_file)
        if ext in ['.ttl']:
            self._ontology_parser_function = lambda s: rdflib.Graph().parse(s, format='n3')
        else:
            self._ontology_parser_function = lambda s: pyRdfa().graph_from_source(s)

        errorstring = "Are you calling parse_ontology from the base SchemaDef class?"
        if not self._ontology_parser_function:
            raise ValueError("No function found to parse ontology. %s" % errorstring)
        if not self._ontology_file:
            raise ValueError("No ontology file specified. %s" % errorstring)
        if not self.lexicon:
            raise ValueError("No lexicon object assigned. %s" % errorstring)

        latest_file = self._pull_standard()

        try:
            self.graph = self._ontology_parser_function(latest_file)
        except:
            raise IOError("Error parsing ontology at %s" % latest_file)

        for subj, pred, obj in self.graph:
            self.ontology[subj].append((pred, obj))
            yield (subj, pred, obj)

    def parse_ontology(self):
        for subj, pred, obj in self._schema_nodes():
            leaves = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                leaves = deepest_node((subj, pred, obj), self.graph)

            for s,p,o in leaves:
                if pred == rt.URIRef(self.lexicon['domain']):
                    self.attributes_by_class[o].append(subj)


# Implementation-specific subclasses
class RdfSchemaDef(SchemaDef):
    def __init__(self):
        super(RdfSchemaDef, self).__init__()
        self.lexicon = {
            'range': "http://www.w3.org/2000/01/rdf-schema#range",
            'domain': "http://www.w3.org/2000/01/rdf-schema#domain",
            'type': "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            'subclass': "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        }


class MicrodataSchemaDef(SchemaDef):
    def __init__(self):
        super(MicrodataSchemaDef, self).__init__()
        self.lexicon = {
            'range': "http://schema.org/range",
            'domain': "http://schema.org/domain",
            'type': "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            'subclass': "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        }
