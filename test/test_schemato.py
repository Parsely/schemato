import pytest

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from schemato import Schemato


class SchematoObjectTest():
    def assert_no_validation_errors(self, doc):
        sc = Schemato(doc)
        res = sc.validate()
        assert all([len(a.warnings) == 0 and len(a.errors) == 0 for a in res])

class TestSchemato(SchematoObjectTest):
    def test_rdfa_no_errors(self):
        self.assert_no_validation_errors("schemato/test_documents/rdf.html")

    def test_schemaorg_no_errors(self):
        self.assert_no_validation_errors("schemato/test_documents/schema.html")
