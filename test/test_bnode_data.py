"""
test_bnode_data.py
Date: 16/05/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

import unittest

import pathlib
import rdflib
import logging

import rdf2g
from test import STREAM_WITH_BNODES


class MyTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        self.longMessage = True  # Print complete error message

        self.rdf_graph = rdflib.Graph()
        self.rdf_graph.parse(str(STREAM_WITH_BNODES), format="n3")
        logging.info('%s triples loaded into RDF graph' % str(len(self.rdf_graph)))
        self.g = rdf2g.setup_graph()

    def test_loading(self):
        rdf2g.clear_graph(self.g)
        rdf2g.load_rdf2g(self.g, self.rdf_graph)
        assert len(self.g.V().toList()) > 0, "Nodes have not been created "
        assert len(self.g.E().toList()) > 0, "Edges have not been created "

    def test_operations(self):
        known_label = "http://sample.igsn.org/soilarchive/bqs2dj2u6s73o70jcpr0"
        node = rdf2g.get_node(self.g, known_label)
        tree = rdf2g.generate_traversal_tree(self.g, node, max_depth=1)
        print(tree)


if __name__ == '__main__':
    unittest.main()
