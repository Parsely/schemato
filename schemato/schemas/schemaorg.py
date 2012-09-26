from validator import MicrodataValidator
from schemadef import MicrodataSchemaDef

class SchemaOrgSchemaDef(MicrodataSchemaDef):
    def __init__(self):
        super(SchemaOrgSchemaDef, self).__init__()
        self._ontology_file = "http://schema.org/docs/schema_org_rdfa.html"

class SchemaOrgValidator(MicrodataValidator):
    pass
