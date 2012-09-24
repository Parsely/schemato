class SchemaDef(object):
    def __init__(self):
        super(SchemaDef, self).__init__()

    def parse_ontology(self):
        """parse the ontology file assigned to this object
        into its ontologygraph member using the appropriate parser"""
        raise NotImplementedError

class RdfSchemaDef(SchemaDef):
    pass

class MicrodataSchemaDef(SchemaDef):
    pass
