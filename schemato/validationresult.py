class ValidationResult(object):
    def __init__(self):
        super(ValidationResult, self).__init__()
        self.warnings = []

    def add_warning(self, string):
        self.warnings.append(ValidationWarning(2, string))

    def add_error(self, string):
        self.warnings.append(ValidationWarning(1, string))


class ValidationWarning(object):
    def __init__(self, level, string):
        super(ValidationWarning, self).__init__()
        self.level = level # can be warning, error (enforce)
        self.string = string
