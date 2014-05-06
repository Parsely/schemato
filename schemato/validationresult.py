import json


class ValidationResult(object):
    ERROR = 1
    WARNING = 2

    def __init__(self, namespace):
        super(ValidationResult, self).__init__()
        self.warnings = []
        self.errors = []
        self.namespace = namespace

    def add_error(self, warning):
        if warning.level == ValidationResult.WARNING:
            self.warnings.append(warning)
        elif warning.level == ValidationResult.ERROR:
            self.errors.append(warning)

    def to_json(self):
        mapping = self.to_dict()
        return json.dumps(mapping)

    def to_dict(self):
        mapping = {}
        mapping['warnings'] = []
        for warning in self.warnings:
            mapping['warnings'].append(warning.to_dict())
        mapping['errors'] = []
        for error in self.errors:
            mapping['errors'].append(error.to_dict())
        mapping['namespace'] = self.namespace
        return mapping


class ValidationWarning(object):
    def __init__(self, level, string, line, line_num):
        super(ValidationWarning, self).__init__()
        self.level = level
        self.string = string
        self.line_num = line_num
        self.line_text = line

    def to_dict(self):
        mapping = {}
        mapping['level'] = "Error" if self.level == ValidationResult.ERROR else "Warning"
        mapping['string'] = self.string
        mapping['line'] = self.line_text
        mapping['num'] = self.line_num
        return mapping


    def to_json(self):
        mapping = self.to_dict()
        return json.dumps(mapping)
