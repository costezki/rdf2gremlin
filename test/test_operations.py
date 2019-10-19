"""
test_operations
Date: 11.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import unittest

import pathlib
import rdflib
import logging

import rdf2g

from gremlin_python.structure.graph import Vertex

OUTPUT_FILE_LAM_PROPERTIES = (
            pathlib.Path(__file__).resolve().parent.parent / "resource/celex_project_properties_v2.ttl").resolve()


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
        known_iri_str = "http://publications.europa.eu/resources/authority/celex/md_OJ_ID"

        assert isinstance(rdf2g.get_node(self.g, skos_concept_iri), Vertex), "The node is not found; 1"
        assert isinstance(rdf2g.get_node(self.g, skos_concept_label), Vertex), "The node is not found; 2"
        assert isinstance(rdf2g.get_node(self.g, skos_concept_id), Vertex), "The node is not found; 3"
        assert isinstance(rdf2g.get_node(self.g, skos_concept_node), Vertex), "The node is not found; 4"

        assert isinstance(rdf2g.get_node(self.g, known_iri_str), Vertex), "The node is not found"

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
        # Expecting this result
        # {'@type': 'g:Tree',
        #  '@value': [{'key': v[864],
        #              'value': {'@type': 'g:Tree',
        #                        '@value': [{'key': e[947][864-rdf:type->880],
        #                                    'value': {'@type': 'g:Tree',
        #                                              '@value': [{'key': v[880],
        #                                                          'value': {'@type': 'g:Tree',
        #                                                                    '@value': []}}]}},
        #                                   {'key': e[903][864-skos:inScheme->899],
        #                                    'value': {'@type': 'g:Tree',
        #                                              '@value': [{'key': v[899],
        #                                                          'value': {'@type': 'g:Tree',
        #                                                                    '@value': []}}]}},
        #                                   {'key': e[942][864-sh:path->940],
        #                                    'value': {'@type': 'g:Tree',
        #                                              '@value': [{'key': v[940],
        #                                                          'value': {'@type': 'g:Tree',
        #                                                                    '@value': []}}]}}]}}]}
        assert tree, "Nothing returned"
        assert tree["@value"], "Unexpected tree structure"
        assert tree["@value"][0]["value"], "Unexpected tree structure"
        assert 4 > len(tree["@value"][0]["value"]["@value"]) > 2, "Unexpected tree structure"
        assert tree["@value"][0]["value"]["@value"][1]["value"], "Unexpected tree structure"


if __name__ == '__main__':
    unittest.main()
