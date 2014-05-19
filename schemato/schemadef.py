import rdflib.term as rt
import logging as log

from rdflib.plugins.parsers.pyRdfa import pyRdfa
import rdflib
import os
import time
import urllib2

from collections import defaultdict

from utils import deepest_node
import settings


# what functionality is common to every single schema def?
class SchemaDef(object):
    """class to handle the loading and caching of a standard
    ASSUMPTIONS:
        This class holds the definition of a standard
        It does not perform any validation against that standard
        This class knows nothing about the input file being validated
    """

    errorstring_base = "Are you calling parse_ontology from the base SchemaDef class?"

    def __init__(self):
        super(SchemaDef, self).__init__()
        self._ontology_file = ""
        self.ontology = defaultdict(list)
        self.attributes_by_class = {}
        self._ontology_parser_function = None
        self.lexicon = {}

    def _read_schema(self):
        """return the local filename of the definition file for this schema
        if not present or older than expiry, pull the latest version from
        the web at self._ontology_file"""
        cache_filename = os.path.join(settings.CACHE_ROOT, "%s.smt" % self._representation)
        log.info("Attempting to read local schema at {}".format(cache_filename))
        try:
            if time.time() - os.stat(cache_filename).st_mtime > settings.CACHE_EXPIRY:
                log.warning("Cache expired, re-pulling")
                self._pull_schema_definition(cache_filename)
        except OSError:
            log.warning("Local schema not found. Pulling from web.")
            self._pull_schema_definition(cache_filename)
        else:
            log.info("Success")

        return cache_filename

    def _pull_schema_definition(self, fname):
        """download an ontology definition from the web"""
        std_url = urllib2.urlopen(self._ontology_file)
        cached_std = open(fname, "w+")
        cached_std.write(std_url.read())
        cached_std.close()

    def parse_ontology(self):
        """place the ontology graph into a set of custom data structures
        for use by the validator"""
        start = time.clock()
        log.info("Parsing ontology file for {}".format(self.__class__.__name__))
        for subj, pred, obj in self._schema_nodes():
            if subj not in self.attributes_by_class.keys():
                if obj == rt.URIRef(self.lexicon['class']) and pred == rt.URIRef(self.lexicon['type']):
                    self.attributes_by_class[subj] = []

            leaves = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                leaves = deepest_node((subj, pred, obj), self.graph)

            for s, p, o in leaves:
                if o not in self.attributes_by_class.keys():
                    self.attributes_by_class[o] = []
                if pred == rt.URIRef(self.lexicon['domain']):
                    self.attributes_by_class[o].append(subj)
        log.info("Ontology parsing complete in {}".format((time.clock() - start) * 1000))

    def _schema_nodes(self):
        """parse self._ontology_file into a graph"""
        name, ext = os.path.splitext(self._ontology_file)
        if ext in ['.ttl']:
            self._ontology_parser_function = lambda s: rdflib.Graph().parse(s, format='n3')
        else:
            self._ontology_parser_function = lambda s: pyRdfa().graph_from_source(s)
        if not self._ontology_parser_function:
            raise ValueError("No function found to parse ontology. %s" % errorstring_base)
        if not self._ontology_file:
            raise ValueError("No ontology file specified. %s" % errorstring_base)
        if not self.lexicon:
            raise ValueError("No lexicon object assigned. %s" % errorstring_base)

        latest_file = self._read_schema()

        try:
            self.graph = self._ontology_parser_function(latest_file)
        except:
            raise IOError("Error parsing ontology at %s" % latest_file)

        for subj, pred, obj in self.graph:
            self.ontology[subj].append((pred, obj))
            yield (subj, pred, obj)


# Implementation-specific subclasses
class RdfSchemaDef(SchemaDef):
    def __init__(self):
        super(RdfSchemaDef, self).__init__()
        # TODO - certainly not the best way to do this, should probably use the
        # pyRdfa/pyMicrodata graph APIs to make this more robust
        self.lexicon = {
            'range': "http://www.w3.org/2000/01/rdf-schema#range",
            'domain': "http://www.w3.org/2000/01/rdf-schema#domain",
            'type': "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            'subclass': "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            'class': "http://www.w3.org/2002/07/owl#Class"
        }


class MicrodataSchemaDef(SchemaDef):
    def __init__(self):
        super(MicrodataSchemaDef, self).__init__()
        # TODO - certainly not the best way to do this, should probably use the
        # pyRdfa/pyMicrodata graph APIs to make this more robust
        self.lexicon = {
            'range': "http://schema.org/rangeIncludes",
            'domain': "http://schema.org/domainIncludes",
            'type': "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            'subclass': "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            'class': "http://www.w3.org/2000/01/rdf-schema#Class"
        }
