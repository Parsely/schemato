from rdflib.plugins.parsers.pyMicrodata import pyMicrodata
from rdflib.plugins.parsers.pyRdfa import pyRdfa


class CompoundGraph(object):
    def __init__(self, source):
        super(CompoundGraph, self).__init__()
        try:
            self.microdata_graph = pyMicrodata().graph_from_source(source)
        except:
            self.microdata_graph = None

        try:
            self.rdfa_graph = pyRdfa().graph_from_source(source)
        except:
            self.rdfa_graph = None
