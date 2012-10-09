import rdflib.term as rt

from validator import RdfValidator
from schemadef import RdfSchemaDef
from utils import deepest_node

class OpenGraphSchemaDef(RdfSchemaDef):
    def __init__(self, url):
        super(OpenGraphSchemaDef, self).__init__()
        self.source = url
        self._ontology_file = "http://ogp.me/ns/ogp.me.ttl"
        self.parse_ontology()

    def parse_ontology(self):
        for subj, pred, obj in self._schema_nodes():
            leaves = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                leaves = deepest_node((subj, pred, obj), self.graph)

            for s,p,o in leaves:
                if s not in self.attributes_by_class[self.source] and not isinstance(s, rt.BNode):
                    self.attributes_by_class[self.source].append(s)

class OpenGraphValidator(RdfValidator):
    def __init__(self, graph, doc_lines, url):
        super(OpenGraphValidator, self).__init__(graph, doc_lines)
        self.source = url
        self.schema_def = OpenGraphSchemaDef(url)
        self.namespace = "http://ogp.me/ns#"
