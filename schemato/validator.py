import rdflib.term as rt
import logging as log

from pyRdfa import pyRdfa
from pyMicrodata import pyMicrodata

from errors import error_line, _error

class SchemaValidator(object):
    """ASSUMPTIONS:
        This class knows about the file being validated, but it recieves that
        file as a graph and a doc_lines
        It does not perform any parsing logic on the file
        It recieves a "validatable" object and returns errors
    """
    def __init__(self, graph, doc_lines):
        super(SchemaValidator, self).__init__()
        self.schema_def = None
        self.used_namespaces = []
        self.allowed_namespaces = []
        self.graph = graph # a CompoundGraph
        log.info("init validator: %s" % self.graph)
        self.doc_lines = doc_lines

    def validate(self):
        errorstring = "Are you calling validate from the base SchemaValidator class?"

        log.info("-------------------------------------------------------------------")
        log.info("Validating against %s" % self.schema_def.__class__.__name__)
        if not self.schema_def:
            raise ValueError("No schema definition supplied. %s" % errorstring)
        if not self.graph:
            raise ValueError("No graph object found to validate!")

        log.info("in validator.validate: %s" % self.graph)

        errors = []
        self.checked_attributes = []
        for s,p,o in self.graph:
            log.info("")
            log.info("subj: " + s)
            log.info("pred: " + p)
            log.info("obj: " + o)
            error = self._check_triple((s,p,o))
            if error and error not in errors:
                errors.append(error)
        # should return a ValidationResult object
        return errors

    def _check_triple(self, (subj, pred, obj)):
        """take a triple and compare it to the ontology, return indication
        of whether it's adherent or not"""
        # don't bother with special 'type' triples
        if self._field_name_from_uri(pred) in ['type', 'item', 'first', 'rest']:
            log.info("ignoring triple with field %s" % self._field_name_from_uri(pred))
            return
        #if self._namespace_from_uri(pred) not in self.used_namespaces:
        #    log.info("unknown namespace %s for triple, discarding" % self._namespace_from_uri(pred))
        #    return

        classes = []
        log.warning("Valid member %s found" % pred)

        instanceof = self._is_instance((subj, pred, obj))

        # this method should differentiate between an "error" and a "warning"
        # since not all issues with an implementation worth telling
        # the user about are actual "errors", just things to keep in mind
        class_invalid = self._validate_class(instanceof)
        if class_invalid:
            log.warning("Invalid class %s" % instanceof)
            return class_invalid

        classes = self._superclasses_for_subject(self.graph, instanceof)
        classes.append(instanceof)

        # is this attribute a valid member of the class or superclasses?
        # in the case of OG, this just means "is it a valid og field"
        member_invalid = self._validate_member(pred, classes, instanceof)
        if member_invalid:
            log.warning("Invalid member of class")
            return member_invalid

        dupe_invalid = self._validate_duplication((subj, pred), instanceof)
        if dupe_invalid:
            log.warning("Duplication found")
            return dupe_invalid

        # collect a list of checked attributes
        self.checked_attributes.append((subj,pred))

        log.warning("successfully validated triple, no errors")

        return

    def _validate_class(self, cl):
        """return error if class `cl` is not found in the ontology"""
        raise NotImplementedError

    def _validate_member(self, member, classes, instanceof):
        """return error if `member` is not a member of any class in `classes`"""
        # for each namespace this validator knows about
        # this causes false errors for standards with multiple valid namespaces
        log.info("Validating member %s" % member)
        if member not in sum([self.schema_def.attributes_by_class[cl] for cl in classes], []):
            return _error("{0} - invalid member of {1}",
                self._field_name_from_uri(member), self._field_name_from_uri(instanceof),
                doc_lines=self.doc_lines)

    def _validate_duplication(self, (subj, pred), cl):
        """returns error if we've already seen the member `pred` on `subj`"""
        log.info("Validating duplication of member %s" % pred)
        if (subj,pred) in self.checked_attributes:
            return _error("{0} - duplicated member of {1}", self._field_name_from_uri(pred),
                self._field_name_from_uri(cl), doc_lines=self.doc_lines)

    def _superclasses_for_subject(self, graph, typeof):
        """helper, returns a list of all superclasses of a given class"""
        classes = []
        superclass = typeof
        while True:
            found = False
            for (p, o) in self.schema_def.ontology[superclass]:
                if self.schema_def.lexicon['subclass'] == str(p):
                    found = True
                    classes.append(o)
                    superclass = o
            if not found:
                break
        return classes

    def _is_instance(self, (subj, pred, obj)):
        """helper, returns the class type of subj"""
        for s,p,o in self.graph:
            if s == subj and str(p) == self.schema_def.lexicon['type']:
                return o
        return None

    def _field_name_from_uri(self, uri):
        """helper, returns the name of an attribute (without namespace prefix)"""
        uri = str(uri)
        parts = uri.split('#')
        if len(parts) == 1:
            return uri.split('/')[-1]
        return parts[-1]

    def _namespace_from_uri(self, uri):
        """returns the expanded namespace prefix of a uri"""
        uri = str(uri)
        parts = uri.split('#')
        if len(parts) == 1:
            return "%s/" % '/'.join(uri.split('/')[:-1])
        return "%s#" % '#'.join(parts[:-1])

    def _find_namespaces(self, doc_lines):
        for ns in self.allowed_namespaces:
            self.used_namespaces.append(ns)

# what functionality do rdf and microdata validation not share
class RdfValidator(SchemaValidator):
    def __init__(self, graph, doc_lines):
        super(RdfValidator, self).__init__(graph, doc_lines)
        self.parser = pyRdfa()
        self.graph = self.graph.rdfa_graph
        log.info("in RdfValidator init %s" % self.graph)

    def _validate_class(self, cl):
        if cl not in self.schema_def.attributes_by_class.keys():
            search_string = self._field_name_from_uri(cl)
            return _error("{0} - invalid class", self._field_name_from_uri(cl),
                search_string=search_string, doc_lines=self.doc_lines)


class MicrodataValidator(SchemaValidator):
    def __init__(self, graph, doc_lines):
        super(MicrodataValidator, self).__init__(graph, doc_lines)
        self.parser = pyMicrodata()
        self.graph = self.graph.microdata_graph

    def _validate_class(self, cl):
        if cl not in self.schema_def.attributes_by_class.keys():
            search_string = str(cl)
            return _error("{0} - invalid class", self._field_name_from_uri(cl),
                search_string=search_string, doc_lines=self.doc_lines)

