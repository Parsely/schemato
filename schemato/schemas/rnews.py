from validator import RdfValidator
from schemadef import RdfSchemaDef

class RNewsValidator(RdfValidator):
    def __init__(self):
        super(RNewsValidator, self).__init__()
        self.schema_def = RNewsSchemaDef()
        self.namespace = "http://iptc.org/std/rNews/2011-10-07#"

class RNewsSchemaDef(RdfSchema):
    def __init__(self):
        super(RNewsSchemaDef, self).__init__()
        self._ontology_file = "http://dev.iptc.org/files/rNews/rnews_1.0_draft3_rdfxml.owl"
        # needs to be called after super
        # use of this object requires it
        self.parse_ontology()

