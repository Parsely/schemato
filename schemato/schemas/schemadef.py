# what functionality is common to every single schema def?
class SchemaDef(object):
    def __init__(self):
        super(SchemaDef, self).__init__()
        self.ontology_file = ""
        self.ontology_graph = None
        self.ontology_parser_function = None

    def parse_ontology(self):
        """ABSTRACT - parse the ontology file into a graph"""
        raise NotImplementedError

# what separate functionality does an RdfSchemaDef have
# from a MicrodataSchemaDef?
class RdfSchemaDef(SchemaDef):
    pass

class MicrodataSchemaDef(SchemaDef):
    pass
