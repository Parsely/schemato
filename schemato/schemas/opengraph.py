from validator import RdfValidator
from schemadef import RdfSchemaDef

class OpenGraphSchemaDef(RdfSchemaDef):
    def __init__(self):
        super(OpenGraphSchemaDef, self).__init__()
        self._ontology_file = "http://ogp.me/ns/ogp.me.ttl"

    def parse_ontology(self):
        for subj, pred, obj in self._schema_nodes()
            leaves = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                leaves = deepest_node((subj, pred, obj), graph)

            for s,p,o in leaves:
                if s not in self.attribs_by_class[self.source] and not isinstance(s, rt.BNode):
                    self.attribs_by_class[self.source].append(s)

class OpenGraphValidator(RdfValidator):
    pass
