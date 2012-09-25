from validator import RdfValidator
from schemadef import RdfSchemaDef

class RNewsValidator(RdfValidator):
    schema = RNewsSchema()
    pass

class RNewsSchema(RdfSchema):
    pass
