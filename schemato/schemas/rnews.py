from validator import RdfValidator
from schemadef import RdfSchemaDef


class RNewsValidator(RdfValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(RNewsValidator, self).__init__(graph, doc_lines, url=url)
        self.schema_def = RNewsSchemaDef()
        self.allowed_namespaces = ["http://iptc.org/std/rNews/2011-10-07#"]


class RNewsSchemaDef(RdfSchemaDef):
    def __init__(self):
        super(RNewsSchemaDef, self).__init__()
        self._ontology_file = "http://dev.iptc.org/files/rNews/rnews_1.0_draft3_rdfxml.owl"
        self._representation = "rnews_schemadef"
