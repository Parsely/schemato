from validator import MicrodataValidator
from schemadef import MicrodataSchemaDef


class SchemaOrgSchemaDef(MicrodataSchemaDef):
    def __init__(self):
        super(SchemaOrgSchemaDef, self).__init__()
        self._ontology_file = "http://schema.org/docs/schema_org_rdfa.html"
        self._representation = "schemaorg_schemadef"


class SchemaOrgValidator(MicrodataValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(SchemaOrgValidator, self).__init__(graph, doc_lines, url=url)
        self.schema_def = SchemaOrgSchemaDef()
        self.allowed_namespaces = ["http://schema.org/"]
