import rdflib.term as rt
from pyMicrodata import pyMicrodata
from pyRdfa import pyRdfa
import rdflib

from collections import defaultdict


# what functionality is common to every single schema def?
class SchemaDef(object):
    """class to handle the loading and caching of a standard"""
    def __init__(self):
        super(SchemaDef, self).__init__()
        self.ontology_file = ""
        self.ontology = defaultdict(list)
        self.attributes_by_class = defaultdict(list)
        self.ontology_parser_function = None

    def parse_ontology(self):
        """parse the ontology file into a graph"""
        # problem: it makes sense to have this implementation be common
        # between the below two subclasses (ie have it implemented here)
        # however, it depends on ontology_parser_function being set,
        # which happens in the subclasses. maybe no big deal, but worth being
        # thoughtful about
        raise NotImplementedError

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
