"""
operations
Date: 11.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import logging
import os

import rdflib
from gremlin_python import statics
from gremlin_python.structure.graph import Graph, Vertex, Edge, Element
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import T, P, Operator, Bindings
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

from rdf2g.retrieve import *


def load_rdf2g(g, rdf_graph):
    """
        Load an RDF graph into a property graph g
    :param g: gremlin graph
    :param rdf_graph: rdf graph
    :return: gremlin graph
    """
    for s, p, o in rdf_graph:
        subj_node = create_node(g, s, rdf_graph)
        if isinstance(o, (rdflib.URIRef, rdflib.BNode)):
            obj_node = create_node(g, o, rdf_graph)
            link_nodes(g, subj_node, obj_node, p, rdf_graph)
        elif isinstance(o, rdflib.Literal):
            add_property(g, node=subj_node, property_term=p, value_term=o, rdf_graph=rdf_graph)
    return g


def clear_graph(g):
    """
        erase all the vertices and edges from a graph
    :param g:
    :return:
    """
    # g = setup_graph()
    logging.info('Cleaning up the graph.')
    g.V().drop().iterate()
    return True


def create_node(g, rdf_term, rdf_graph):
    """
        Add a new node to the graph.
    :param g: gremlin graph
    :param rdf_term:  the rdf_term identifying the node
    :param rdf_graph: the graph to which rdf_term belongs
    :return: the newly created node
    """

    # pg = g if g else setup_graph()

    # if already exists, do not add a new node
    existing_node = get_node(g, rdf_term)
    if existing_node:
        logging.debug('Node exists.')
        return existing_node

    logging.debug('Adding a new node to the graph.')
    label = rdf_graph.qname(rdf_term) if rdf_graph.qname(rdf_term) else str(rdf_term)
    iri = str(rdf_term)
    return g.addV(label).property('iri', iri).next()


def add_property(g, node, property_term, value_term, rdf_graph):
    """
        Add or overwrite the property of a graph node
    :param g: gremlin graph
    :param node: gremlin node
    :param property_term: property label rdf term
    :param value_term: the value rdf term
    :param rdf_graph: the RDF graph
    :return: the enriched node
    """
    logging.debug('Adding a new property to the graph.')
    # pg = g if g else setup_graph()
    if isinstance(property_term, rdflib.URIRef) and rdf_graph:
        property_label = rdf_graph.qname(property_term) if rdf_graph.qname(property_term) else str(
            property_term)
    else:
        property_label = str(property_term)
    property_value = str(value_term)

    return g.V(node).property(property_label, property_value).next()


def link_nodes(g, source_node, target_node, property_term, rdf_graph):
    """
        establish a new link/edge between two existent nodes
    :param g: gremlin graph
    :param source_node: from gremlin node
    :param target_node: to gremlin node
    :param property_term: edge label rdf term
    :param rdf_graph: the RDF graph
    :return: the newly created edge
    """
    # pg = g if g else setup_graph()
    if isinstance(property_term, rdflib.URIRef) and rdf_graph:
        property_label = rdf_graph.qname(property_term) if rdf_graph.qname(property_term) else str(
            property_term)
    else:
        property_label = str(property_term)

    logging.debug('Adding the link "%s" from %s to %s.' % (str(property_label), str(source_node), str(target_node)))

    return g.V(Bindings.of('id', source_node)).addE(property_label).to(target_node).iterate()
