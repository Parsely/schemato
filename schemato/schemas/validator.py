class SchemaValidator(object):
    def __init__(self):
        super(SchemaValidator, self).__init__()

    def validate(self):
        """ABSTRACT - perform the validation logic for a schema"""
        raise NotImplementedError

class RdfValidator(SchemaValidator):
    pass

class MicrodataValidator(SchemaValidator):
    pass



