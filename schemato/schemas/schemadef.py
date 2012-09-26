import rdflib.term as rt
from pyMicrodata import pyMicrodata
from pyRdfa import pyRdfa
import rdflib

from collections import defaultdict

from utils import deepest_node


# what functionality is common to every single schema def?
class SchemaDef(object):
    """class to handle the loading and caching of a standard"""
    def __init__(self):
        super(SchemaDef, self).__init__()
        self.ontology_file = ""
        self.ontology = defaultdict(list)
        self.attributes_by_class = defaultdict(list)
        self.ontology_parser_function = None
        self.lexicon = None

    def parse_ontology(self):
        for subj, pred, obj in self._schema_nodes()
            leaves = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                leaves = deepest_node((subj, pred, obj), graph)

            for s,p,o in leaves:
                if pred == rt.URIRef(self.domain_uri):
                    self.attributes_by_class[o].append(subj)

    def _schema_nodes(self):
        # test commit
        """parse the ontology file into a graph"""

        errorstring = "Are you calling parse_ontology from the base SchemaDef class?"
        if not self.ontology_parser_function:
            raise ValueError("No function found to parse ontology. %s" % errorstring)
        if not self.ontology_file:
            raise ValueError("No ontology file specified. %s" % errorstring)
        if not self.lexicon:
            raise ValueError("No lexicon object assigned. %s" % errorstring)

        try:
            graph = self.ontology_parser_function(self.ontology_file)
        except:
            raise IOError("Error parsing ontology %s" % self.ontology_file)

        for subj, pred, obj in graph:
            self.ontology[subj].append((pred, obj))
            yield (subj, pred, obj)


# what separate functionality does an RdfSchemaDef have
# from a MicrodataSchemaDef?
class RdfSchemaDef(SchemaDef):
    def __init__(self):
        super(RdfSchemaDef, self).__init__()
        self.ontology_parser_function = lambda s: rdflib.Graph().parse(s, format='n3')


class MicrodataSchemaDef(SchemaDef):
    def __init__(self):
        super(MicrodataSchemaDef, self).__init__()
        self.ontology_parser_function = lambda s: pyRdfa().graph_from_source(s)
