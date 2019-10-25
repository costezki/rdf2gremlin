"""
test_graph_creation
Date: 13.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import unittest

import pathlib
import rdflib
import logging

import rdf2g
from test import OUTPUT_FILE_LAM_PROPERTIES


class MyTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        self.longMessage = True  # Print complete error message

        self.rdf_graph = rdflib.Graph()
        self.rdf_graph.parse(str(OUTPUT_FILE_LAM_PROPERTIES), format="ttl")
        logging.info('%s triples loaded into RDF graph' % str(len(self.rdf_graph)))
        self.g = rdf2g.setup_graph()

    def test_add_nodes(self):
        for s, p, o in self.rdf_graph:
            subj_node = rdf2g.create_node(self.g, s, self.rdf_graph)
            if isinstance(o, (rdflib.URIRef, rdflib.BNode)):
                obj_node = rdf2g.create_node(self.g, o, self.rdf_graph)
                rdf2g.link_nodes(self.g, subj_node, obj_node, p, self.rdf_graph)
            elif isinstance(o, rdflib.Literal):
                rdf2g.add_property(self.g, node=subj_node, property_term=p, value_term=o, rdf_graph=self.rdf_graph)

        assert len(self.g.V().toList()) > 0, "Nodes have not been created "

    def test_load_rdf(self):
        rdf2g.clear_graph(self.g)
        rdf2g.load_rdf2g(self.g, self.rdf_graph)
        assert len(self.g.V().toList()) > 0, "Nodes have not been created "
        assert len(self.g.E().toList()) > 0, "Edges have not been created "

    def test_clear(self):
        rdf2g.clear_graph(self.g)
        assert len(self.g.V().toList()) == 0, "The graph is not empty"
        # rdf2g.load_rdf2g(self.g, self.rdf_graph)


if __name__ == '__main__':
    unittest.main()
