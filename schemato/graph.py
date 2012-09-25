import rdflib.term as rt
from pyMicrodata import pyMicrodata
from pyRdfa import pyRdfa
import rdflib

from errors import _error

from collections import defaultdict
import os
from settings import *


def deepest_node((subj, pred, obj), graph):
    """recurse down the tree and return a list of the most deeply nested
    child nodes of the given triple"""
    # i don't fully accept the premise that this docstring presents
    # i'm not a docstring literalist
    to_return = []
    def _deepest_node((subj, pred, obj), graph):
        children = []
        if isinstance(obj, rt.BNode):
            for s,p,o in graph:
                if str(s) == str(obj):
                    children.append((s,p,o))
            for s,p,o in children:
                s1,p1,o1 = _deepest_node((s, p, o), graph)
                # coupling *smacks hand with ruler*
                if "rNews" in str(o1) and (s1,p1,o1) not in to_return:
                    to_return.append((s1,p1,o1))
            return (s1,p1,o1)
        else:
            return (subj, pred, obj)
    _deepest_node((subj, pred, obj), graph)
    return to_return


class Graph(object):
    """a graph may have multiple ontologies but must have exactly one self.graph"""
    # the concept of a graph object should probably still exist at some level,
    # but it will be more deeply nested within abstractions
    def __init__(self, url, impl):
        self.ns_ont = {}
        self.attribs_by_class = defaultdict(list)
        self.ontologies = [] # are these initializations necessary
        self.attributes = []
        self.source = url
        self.impl = impl
        if 'rdfa' == impl:
            self.range_uri = "http://www.w3.org/2000/01/rdf-schema#range"
            self.domain_uri = "http://www.w3.org/2000/01/rdf-schema#domain"
            self.type_uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            self.subclass_uri = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
            self.parser = pyRdfa()
        elif 'microdata' == impl:
            self.range_uri = "http://schema.org/range"
            self.domain_uri = "http://schema.org/domain"
            self.type_uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            self.subclass_uri = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
            self.parser = pyMicrodata()
        return super(Graph, self).__init__()

    ####################################################################
    #                         MAIN FRONTENDS                           #
    ####################################################################
    def check(self, doc_lines):
        """iterates over self.graph, calling check_triple on each triple
        tracks the errors and returns a list thereof"""
        self.doc_lines = doc_lines
        errors = []
        for s,p,o in self.graph:
            error = self.check_triple((s,p,o))
            if error and error not in errors:
                errors.append(error)
        return errors

    def build_graph(self):
        """build a graph from the document and assemble the ontologies
        necessary to validate it"""
        self.graph = self.parser.graph_from_source(self.source)

        # this depends on a field that's not set in the constructor, ns_ont
        # it must be set before this function is called. that sucks so much
        for ns in self.ns_ont:
            self.ontologies.append(self.parse_ontology(self.ns_ont[ns]))

        return self

    #####################################################################
    #                        VALIDATION WRAPPERS                        #
    #####################################################################
    def parse_ontology(self, source=None):
        """parse the given ontology into two special data formats
        self.ontology is a dict containing triples of the form {subj: (pred, obj)}
        self.attribs_by_class is a dict like {class: [class_data_members]}
        """
        # this method will probably go into the *SchemaDef classes
        ontology = defaultdict(list)

        parse_func = self.get_filetype(source)

        try:
            # this call takes a really long time when given the schema.org ontology
            graph = parse_func(source)
        except:
            raise IOError('Error parsing ontology %s' % source)

        for subj, pred, obj in graph:
            ontology[subj].append((pred, obj))

            deep_nodes = [(subj, pred, obj)]
            if type(obj) == rt.BNode:
                deep_nodes = deepest_node((subj, pred, obj), graph)

            for s,p,o in deep_nodes:
                if "ogp.me" in source or "opengraph" in source:
                    if s not in self.attribs_by_class[self.source] and not isinstance(s, rt.BNode):
                        self.attribs_by_class[self.source].append(s)
                else:
                    if pred == rt.URIRef(self.domain_uri):
                        self.attribs_by_class[o].append(subj)

        return ontology

    def check_triple(self, (subj, pred, obj)):
        """take a triple and compare it to the ontology, return indication
        of whether it's adherent or not"""
        # don't bother with special 'type' triples
        if self.field_name(pred) in ['type', 'item', 'first', 'rest']:
            return
        if self.namespace_from_uri(pred) not in self.ns_ont.keys():
            return

        classes = []

        instanceof = self.is_instance((subj, pred, obj)) or self.source

        # this method should differentiate between an "error" and a "warning"
        # since not all issues with an implementation worth telling
        # the user about are actual "errors", just things to keep in mind
        class_invalid = self.validate_class(instanceof)
        if class_invalid:
            return class_invalid

        classes = self.superclasses_for_subject(self.graph, instanceof)
        classes.append(instanceof)

        # is this attribute a valid member of the class or superclasses?
        # in the case of OG, this just means "is it a valid og field"
        member_invalid = self.validate_member(pred, classes, instanceof)
        if member_invalid:
            return member_invalid

        dupe_invalid = self.validate_duplication((subj, pred), instanceof)
        if dupe_invalid:
            return dupe_invalid

        # collect a list of checked attributes
        self.attributes.append((subj,pred))

        return

    #################################################################
    #                       VALIDATION BACKENDS                     #
    #################################################################
    def validate_class(self, cl):
        """return error if class `cl` is not found in the ontology"""
        if cl not in self.attribs_by_class.keys():
            search_string = str(cl)
            # this is fishy
            if self.impl != 'microdata':
                search_string = self.field_name(cl)
            return _error("{0} - invalid class", self.field_name(cl),
                search_string=search_string, doc_lines=self.doc_lines)
        return

    def validate_member(self, member, classes, instanceof):
        """return error if `member` is not a member of any class in `classes`"""
        valid = False
        for ns in self.ns_ont.keys():
            name = "%s%s" % (ns, self.field_name(member))
            if rt.URIRef(name) in sum([self.attribs_by_class[cl] for cl in classes], []):
                valid = True
        if not valid:
            return _error("{0} - invalid member of {1}",
                self.field_name(member), self.field_name(instanceof),
                doc_lines=self.doc_lines)
        return

    def validate_duplication(self, (subj, pred), cl):
        """returns error if we've already seen the member `pred` on `subj`"""
        if (subj,pred) in self.attributes:
            return _error("{0} - duplicated member of {1}", self.field_name(pred),
                self.field_name(cl), doc_lines=self.doc_lines)

    #################################################################
    #                      HELPERS / UTILITIES                      #
    #################################################################
    def get_filetype(self, source):
        """returns the function that can be used to parse the given
        document into an rdflib.Graph"""
        name, ext = os.path.splitext(source)
        if ext in ['.ttl']:
            # these should each belong to their respective validator
            def _parse_func(s):
                return rdflib.Graph().parse(s, format='n3')
        else:
            def _parse_func(s):
                return pyRdfa().graph_from_source(s)
        return _parse_func

    def superclasses_for_subject(self, graph, typeof):
        """helper, returns a list of all superclasses of a given class"""
        classes = []
        superclass = typeof
        while True:
            found = False
            for ont in self.ontologies:
                for (p, o) in ont[superclass]:
                    if self.subclass_uri == str(p):
                        found = True
                        classes.append(o)
                        superclass = o
            if not found:
                break
        return classes

    def is_instance(self, (subj, pred, obj)):
        """helper, returns the class type of subj"""
        for s,p,o in self.graph:
            if s == subj and str(p) == self.type_uri:
                return o
        return None

    def field_name(self, uri):
        """helper, returns the name of an attribute (without namespace prefix)"""
        uri = str(uri)
        parts = uri.split('#')
        if len(parts) == 1:
            return uri.split('/')[-1]
        return parts[-1]

    def namespace_from_uri(self, uri):
        """returns the expanded namespace prefix of a uri"""
        uri = str(uri)
        parts = uri.split('#')
        if len(parts) == 1:
            return "%s/" % '/'.join(uri.split('/')[:-1])
        return "%s#" % '#'.join(parts[:-1])

