"""
test_operations
Date: 11.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import unittest

import pathlib
from pprint import pprint

import rdflib
import logging

import rdf2g

from gremlin_python.structure.graph import Vertex

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

    def test_get_node(self):
        skos_concept_iri = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#Concept")
        skos_concept_label = "skos:Concept"
        skos_concept_id = self.g.V().hasLabel(skos_concept_label).toList()[0].id
        skos_concept_node = self.g.V().hasLabel(skos_concept_label).toList()[0]
        # known_iri_str = "http://publications.europa.eu/resources/authority/celex/md_OJ_ID"

        n = rdf2g.get_node(self.g, skos_concept_iri)
        assert isinstance(n, Vertex), "The node is not found; 1"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        n = rdf2g.get_node(self.g, skos_concept_label)
        assert isinstance(n, Vertex), "The node is not found; 2"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        n = rdf2g.get_node(self.g, skos_concept_id)
        assert isinstance(n, Vertex), "The node is not found; 3"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        n = rdf2g.get_node(self.g, skos_concept_node)
        assert isinstance(n, Vertex), "The node is not found; 4"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        # n = rdf2g.get_node(self.g, known_iri_str)
        # assert isinstance(n, Vertex), "The node is not found"

    def test_get_node_1(self):
        skos_concept_iri = rdflib.URIRef(
            "http://publications.europa.eu/resources/authority/lam/res_h9ci2wPXrcUXBh9JkkHzUY")
        skos_concept_label = "lamd:res_h9ci2wPXrcUXBh9JkkHzUY"
        pprint(self.g.V().hasLabel(skos_concept_label).toList())

        skos_concept_id = self.g.V().hasLabel(skos_concept_label).toList()[0].id
        skos_concept_node = self.g.V().hasLabel(skos_concept_label).toList()[0]

        n = rdf2g.get_node(self.g, skos_concept_iri)
        assert isinstance(n, Vertex), "The node is not found; 1"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        n = rdf2g.get_node(self.g, skos_concept_label)
        assert isinstance(n, Vertex), "The node is not found; 2"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        n = rdf2g.get_node(self.g, skos_concept_id)
        assert isinstance(n, Vertex), "The node is not found; 3"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"
        n = rdf2g.get_node(self.g, skos_concept_node)
        assert isinstance(n, Vertex), "The node is not found; 4"
        assert rdf2g.get_node_properties(self.g, n)["@label"] == skos_concept_label, "Wrong label"

    def test_get_node_properties(self):
        known_iri_str = "http://publications.europa.eu/resources/authority/celex/md_OJ_ID"
        n = rdf2g.get_node(self.g, known_iri_str)
        props = rdf2g.get_node_properties(self.g, n)
        assert 'iri' in props, "Expecting 'iri' key among the node properties "

    def test_get_nodes(self):
        assert len(rdf2g.get_nodes(self.g)) > 0, "No node available"

    def test_add_property(self):
        known_iri_str = "http://publications.europa.eu/resources/authority/celex/md_OJ_ID"
        n = rdf2g.get_node(self.g, known_iri_str)

        rdf2g.add_property(self.g, n, "property", "value", self.rdf_graph)
        props = rdf2g.get_node_properties(self.g, n)
        assert 'property' in props, "Expecting 'property' key among the node properties "

        rdf2g.add_property(self.g, n, rdflib.URIRef(known_iri_str), "super value", self.rdf_graph)
        props = rdf2g.get_node_properties(self.g, n)
        assert 'celexd:md_OJ_ID' in props, "Expecting 'celexd:md_OJ_ID' key among the node properties "

    def test_add_edge(self):
        known_iri_str1 = "http://publications.europa.eu/resources/authority/celex/md_OJ_ID"
        known_iri_str2 = "http://www.w3.org/2004/02/skos/core#Concept"
        known_iri_str3 = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        known_iri_str4 = "http://www.w3.org/1999/02/22-rdf-syntax-ns#super-type"

        v1 = rdf2g.get_node(self.g, known_iri_str1)
        v2 = rdf2g.get_node(self.g, known_iri_str2)
        rdf2g.link_nodes(self.g, v1, v2, rdflib.URIRef(known_iri_str3), self.rdf_graph)
        rdf2g.link_nodes(self.g, v1, v2, rdflib.URIRef(known_iri_str4), self.rdf_graph)

    def test_transform_graph(self):
        known_iri = 'http://publications.europa.eu/resources/authority/celex/md_CODE'
        s = self.g.V().has('iri', known_iri).outE().inV().tree().next()
        result = rdf2g.expand_tree(self.g, s)
        assert result, "Nothing returned"
        assert result[0]["@label"] == 'celexd:md_CODE', "Unexpected label %s" % result[0]["@label"]
        assert result[0]["rdf:type"]["@label"] == "skos:Concept", "Unexpected rdf:type label %s" % \
                                                                  result[0]["rdf:type"][
                                                                      "@label"]
        assert result[0]["skos:inScheme"]["@label"] == "lamd:DocumentProperty", "Unexpected label %s" % \
                                                                                result[0]["skos:inScheme"]["@label"]
        assert result[0]["skos:inScheme"]["skos:prefLabel"] == "Document metadata", "Unexpected label %s" % \
                                                                                    result[0]["skos:inScheme"][
                                                                                        "skos:prefLabel"]

    def test_get_nodes_of_type(self):
        skos_concept_iri = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#Concept")
        skos_concept_label = "skos:Concept"
        skos_concept_id = self.g.V().hasLabel(skos_concept_label).toList()[0].id
        skos_concept_node = self.g.V().hasLabel(skos_concept_label).toList()[0]

        assert 9 > len(rdf2g.get_nodes_of_type(self.g, skos_concept_iri)) > 5, "Missing 7 concepts"
        assert 9 > len(rdf2g.get_nodes_of_type(self.g, skos_concept_label)) > 5, "Missing 7 concepts"
        assert 9 > len(rdf2g.get_nodes_of_type(self.g, skos_concept_id)) > 5, "Missing 7 concepts"
        assert 9 > len(rdf2g.get_nodes_of_type(self.g, skos_concept_node)) > 5, "Missing 7 concepts"

    def test_generate_tree(self):
        known_label = "celexd:md_DTN"
        node = rdf2g.get_node(self.g, known_label)
        tree = rdf2g.generate_traversal_tree(self.g, node, max_depth=1)

        assert tree, "Nothing returned"
        assert tree["@value"], "Unexpected tree structure"
        assert tree["@value"][0]["value"], "Unexpected tree structure"
        assert 4 > len(tree["@value"][0]["value"]["@value"]) > 2, "Unexpected tree structure"
        assert tree["@value"][0]["value"]["@value"][1]["value"], "Unexpected tree structure"

    def test_expand_tree_1(self):
        known_label = "celexd:md_DTN"
        node = rdf2g.get_node(self.g, known_label)
        tree = rdf2g.generate_traversal_tree(self.g, node, max_depth=1)

        exp_tree = rdf2g.expand_tree(self.g, tree)
        pprint(exp_tree)

        assert exp_tree, "Nothing returned"
        assert "@id" in exp_tree[0] and "@label" in exp_tree[0], "Unexpected tree structure"
        assert exp_tree[0]["@label"] == known_label, "Unexpected tree structure"
        assert exp_tree[0]["rdf:type"]["@label"] == "skos:Concept", "Unexpected tree structure"

    def test_expand_tree_multi_value(self):
        skos_concept_iri = rdflib.URIRef(
            "http://publications.europa.eu/resources/authority/lam/res_h9ci2wPXrcUXBh9JkkHzUY")
        skos_concept_label = "lamd:res_h9ci2wPXrcUXBh9JkkHzUY"

        node = rdf2g.get_node(self.g, skos_concept_label)
        # pprint(str(node))
        tree = rdf2g.generate_traversal_tree(self.g, node, max_depth=2)
        # pprint(tree)
        exp_tree = rdf2g.expand_tree(self.g, tree)[0]
        # pprint(exp_tree)
        assert isinstance(exp_tree["skos:member"], list), "Expecting multiple members"
        assert "rdf:type" in exp_tree["skos:member"][0], "Expecting an rdf:type [0]"
        assert "rdf:type" in exp_tree["skos:member"][1], "Expecting an rdf:type [1]"
        assert "rdf:type" in exp_tree["skos:member"][2], "Expecting an rdf:type [2]"


if __name__ == '__main__':
    unittest.main()
