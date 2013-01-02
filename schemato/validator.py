import rdflib.term as rt
import logging as log
import sys

from pyRdfa import pyRdfa
from pyMicrodata import pyMicrodata

from errors import error_line, _error
from validationresult import ValidationResult, ValidationWarning
import compound_graph

class SchemaValidator(object):
    """ASSUMPTIONS:
        This class knows about the file being validated, but it recieves that
        file as a graph and a doc_lines
        It does not perform any parsing logic on the file
        It recieves a "validatable" graph object and returns errors"""
    def __init__(self, graph, doc_lines, url=""):
        super(SchemaValidator, self).__init__()
        self.schema_def = None
        self.used_namespaces = []
        self.allowed_namespaces = []

        if isinstance(graph, compound_graph.CompoundGraph):
            self.graph = graph
        else:
            log.error("Validatable graph must be of type CompoundGraph")
            return

        log.info("init validator: %s" % self.graph)
        self.doc_lines = doc_lines

    def validate(self):
        """Iterate over all triples in the graph and validate each one appropriately"""
        errorstring = "Are you calling validate from the base SchemaValidator class?"

        log.info("-------------------------------------------------------------------")
        log.info("Validating against %s" % self.schema_def.__class__.__name__)

        if not self.schema_def:
            raise ValueError("No schema definition supplied. %s" % errorstring)
        if not self.graph:
            raise ValueError("No graph object found to validate!")

        log.info("in validator.validate: %s" % self.graph)

        # TODO - this should choose the actually used namespace, not just
        # the first one in the list
        result = ValidationResult(self.allowed_namespaces[0])

        self.checked_attributes = []
        for s,p,o in self.graph:
            log.info("")
            log.info("subj: " + s)
            log.info("pred: " + p)
            log.info("obj: " + o)
            warning = self._check_triple((s,p,o))
            if warning:
                result.add_error(warning)
        return result

    def _check_triple(self, (subj, pred, obj)):
        """compare triple to ontology, return error or None"""
        # don't bother with special 'type' triples
        if self._field_name_from_uri(pred) in ['type', 'item', 'first', 'rest']:
            log.info("ignoring triple with predicate '%s'" % self._field_name_from_uri(pred))
            return

        classes = []
        log.warning("Possible member %s found" % pred)

        if self._namespace_from_uri(pred) not in self.allowed_namespaces:
            log.info("Member %s does not use an allowed namespace", pred)
            return

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
        # abstract, implemented in subclasses
        raise NotImplementedError

    def _validate_member(self, member, classes, instanceof):
        """return error if `member` is not a member of any class in `classes`"""
        log.info("Validating member %s" % member)

        # TODO - recalculating this list for every member is inefficient
        # calculate it once at the beginning, or consider replacing
        # attributes_by_class with it somehow
        stripped_attribute_names = []
        sublist = []
        for cl in classes:
            for attr in self.schema_def.attributes_by_class[cl]:
                sublist.append(attr)
            for field in sublist:
                sublist[sublist.index(field)] = self._field_name_from_uri(field)
            stripped_attribute_names.append(sublist)

        if self._field_name_from_uri(member) in sum(stripped_attribute_names, []):
            if member in sum([self.schema_def.attributes_by_class[cl] for cl in classes], []):
                log.info("success")
                return None
            elif self._namespace_from_uri(member) in self.allowed_namespaces:
                # TODO - return a warning here - the member's namespace is not found in the
                # official standard, but is included in allowed_namespaces
                log.info("warning - unofficially allowed namespace")
                err = _error("Unoficially allowed namespace {0}",
                    self._namespace_from_uri(member), doc_lines=self.doc_lines)
                return ValidationWarning(ValidationResult.WARNING, err['err'], err['line'], err['num'])
        else:
            log.info("failure")
            err = _error("{0} - invalid member of {1}",
                self._field_name_from_uri(member), self._field_name_from_uri(instanceof),
                doc_lines=self.doc_lines)
            return ValidationWarning(ValidationResult.ERROR, err['err'], err['line'], err['num'])


    def _validate_duplication(self, (subj, pred), cl):
        """returns error if we've already seen the member `pred` on `subj`"""
        # TODO - in general this is not actually an error but a warning
        log.info("Validating duplication of member %s" % pred)
        if (subj,pred) in self.checked_attributes:
            log.info("failure")
            err = _error("{0} - duplicated member of {1}", self._field_name_from_uri(pred),
                self._field_name_from_uri(cl), doc_lines=self.doc_lines)
            return ValidationWarning(ValidationResult.ERROR, err['err'], err['line'], err['num'])
        log.info("success")

    def _superclasses_for_subject(self, graph, typeof):
        """helper, returns a list of all superclasses of a given class"""
        # TODO - this replaces a fairly simple graph API query where it doesn't need to
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
        # TODO - using the graph API could help avoid iterating over every item here
        for s,p,o in self.graph:
            if s == subj and str(p) == self.schema_def.lexicon['type']:
                return o
        return None

    def _field_name_from_uri(self, uri):
        """helper, returns the name of an attribute (without namespace prefix)"""
        # TODO - should use graph API
        uri = str(uri)
        parts = uri.split('#')
        if len(parts) == 1:
            return uri.split('/')[-1] or uri
        return parts[-1]

    def _namespace_from_uri(self, uri):
        """returns the expanded namespace prefix of a uri"""
        # TODO - this could be helped a bunch with proper use of the graph API
        # it seems a bit fragile to treat these as simple string-splits
        uri = str(uri)
        parts = uri.split('#')
        if len(parts) == 1:
            return "%s/" % '/'.join(uri.split('/')[:-1])
        return "%s#" % '#'.join(parts[:-1])

    def _find_namespaces(self, doc_lines):
        # TODO - should be deprecated since it's based on an older paradigm
        for ns in self.allowed_namespaces:
            self.used_namespaces.append(ns)


class RdfValidator(SchemaValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(RdfValidator, self).__init__(graph, doc_lines, url=url)
        self.parser = pyRdfa()
        self.graph = self.graph.rdfa_graph # use the rdfa half of the compound graph

    def _validate_class(self, cl):
        if cl not in self.schema_def.attributes_by_class.keys():
            search_string = self._field_name_from_uri(cl)
            return _error("{0} - invalid class", self._field_name_from_uri(cl),
                search_string=search_string, doc_lines=self.doc_lines)


class MicrodataValidator(SchemaValidator):
    def __init__(self, graph, doc_lines, url=""):
        super(MicrodataValidator, self).__init__(graph, doc_lines, url=url)
        self.parser = pyMicrodata()
        self.graph = self.graph.microdata_graph # use the microdata half of the compound

    def _validate_class(self, cl):
        if cl not in self.schema_def.attributes_by_class.keys():
            search_string = str(cl)
            return _error("{0} - invalid class", self._field_name_from_uri(cl),
                search_string=search_string, doc_lines=self.doc_lines)

