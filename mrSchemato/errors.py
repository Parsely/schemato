def error_line(string, doc_lines=None):
    for line,num in doc_lines:
        if string in line:
            return line,num
    return ('', 0)

def _error(message, *strings, **kwargs):
    for s in strings:
        if not s:
            return None
    search_string = kwargs['search_string'] if 'search_string' in kwargs.keys() else strings[0]
    doc_lines = kwargs['doc_lines']
    message = message.format(*strings)
    line,num = error_line(search_string, doc_lines=doc_lines)
    return {'num': num, 'line': line, 'err': message}
