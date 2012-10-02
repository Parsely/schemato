from pyMicrodata import pyMicrodata
from pyRdfa import pyRdfa
import rdflib


class CompoundGraph(object):
    def __init__(self, source):
        super(CompoundGraph, self).__init__()
        self.microdata_graph = pyMicrodata().graph_from_source(source)
        self.rdf_graph = pyRdfa().graph_from_source(source)
