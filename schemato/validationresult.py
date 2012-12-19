import json


class ValidationResult(object):
    ERROR = 1
    WARNING = 2

    def __init__(self, namespace):
        super(ValidationResult, self).__init__()
        self.warnings = []
        self.namespace = namespace

    def add_error(self, warning):
        self.warnings.append(warning)


class ValidationWarning(object):
    def __init__(self, level, string, line, line_num):
        super(ValidationWarning, self).__init__()
        self.level = level
        self.string = string
        self.line_num = line_num
        self.line_text = line

    def to_json(self):
        mapping = {}
        mapping['level'] = "Error" if self.level == ValidationResult.ERROR else "Warning"
        mapping['string'] = self.string
        mapping['line'] = self.line_text
        mapping['num'] = self.line_num
        return json.dumps(mapping)
