from validator import RdfValidator
from schemadef import RdfSchemaDef


class SchemaOrgRDFaSchemaDef(RdfSchemaDef):
    def __init__(self):
        super(SchemaOrgRDFaSchemaDef, self).__init__()
        self._ontology_file = "http://schema.org/docs/schema_org_rdfa.html"
        self._representation = "schemaorg_schemadef"  # SAME AS MICRODATA VERSION


class SchemaOrgRDFaValidator(RdfValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(SchemaOrgRDFaValidator, self).__init__(graph, doc_lines, url=url)
        self.schema_def = SchemaOrgRDFaSchemaDef()
        self.allowed_namespaces = ["http://schema.org/"]
