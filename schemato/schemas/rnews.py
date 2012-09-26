from validator import RdfValidator
from schemadef import RdfSchemaDef

class RNewsValidator(RdfValidator):
    pass

class RNewsSchemaDef(RdfSchema):
    def __init__(self):
        super(RNewsSchemaDef, self).__init__()
        self._ontology_file = "http://dev.iptc.org/files/rNews/rnews_1.0_draft3_rdfxml.owl"

