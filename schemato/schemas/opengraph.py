from collections import defaultdict
import logging as log
import rdflib.term as rt

from validator import RdfValidator
from schemadef import RdfSchemaDef
from utils import deepest_node

class OpenGraphSchemaDef(RdfSchemaDef):
    def __init__(self, url):
        super(OpenGraphSchemaDef, self).__init__()
        self.source = url
        self._ontology_file = "http://ogp.me/ns/ogp.me.ttl"
        # representation is the filename of the cached local schema
        self._representation = "og_schemadef"
        self.parse_ontology()

    def parse_ontology(self):
        self.attributes_by_class = defaultdict(list, self.attributes_by_class)
        for subj, pred, obj in self._schema_nodes():
            leaves = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                leaves = deepest_node((subj, pred, obj), self.graph)

            for s,p,o in leaves:
                if s not in self.attributes_by_class[self.source] and not isinstance(s, rt.BNode):
                    self.attributes_by_class[self.source].append(s)

class OpenGraphValidator(RdfValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(OpenGraphValidator, self).__init__(graph, doc_lines)
        self.source = url
        self.schema_def = OpenGraphSchemaDef(url)
        self.allowed_namespaces = ["http://ogp.me/ns#", "http://opengraphprotocol.org/schema/"]

    def _is_instance(self, (subj, pred, obj)):
        """helper, returns the class type of subj"""
        return self.source
