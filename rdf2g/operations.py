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
from functools import reduce

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

DEFAULT_LOCAL_CONNECTION_STRING = "ws://localhost:8182/gremlin"


def setup_graph(conn_string=DEFAULT_LOCAL_CONNECTION_STRING):
    """
        Establish the connection to a property graph service using the connection string and return the gremlin graph.
    :param conn_string: connection parameter
    :return: gremlin graph
    """
    try:
        graph = Graph()
        logging.debug('Trying To Connect')
        # new style
        connection = DriverRemoteConnection(conn_string, 'g')
        # The connection should be closed on shut down to close open connections with connection.close()
        g = graph.traversal().withRemote(connection)
        # Reuse 'g' across the application

        logging.info('Successfully connected to the graph server')
    except Exception as e:  # Shouldn't really be so broad
        logging.error(e, exc_info=True)
        raise ("Could not connect to the Gremlin server. Run for example "
               "'docker run --rm --name janusgraph-default janusgraph/janusgraph:latest' OR"
               "'docker run --name gremlin-server -p 8182:8182 tinkerpop/gremlin-server'")
    return g


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


def vertex_to_json(vertex, g):
    # TODO - Almost certainly a better way of doing this
    values = g.V(vertex).valueMap().toList()[0]
    values["id"] = vertex.id
    return values


def flatten_list_of_dicts(list_of_dicts):
    """
        Flatten the list of dictionaries:
        This is an expression for Python 3.5 or greater that merges dictionaries using reduce
        Warning: repeating keys will be overwritten.
    """
    return reduce(lambda x, y: {**x, **y}, list_of_dicts, {})


def get_node(g, id_):
    """
        return the node that is identified by id_
    :param g: remlin graph
    :param id_: the node id or URI
    :return: the node
    """
    if isinstance(id_, (rdflib.URIRef, rdflib.BNode, str)):
        nodes = g.V().has("iri", str(id_)).toList()
    else:
        nodes = g.V(id_).toList()

    # logging.info("Nodes found are: %s" % nodes)

    # If not found
    if not nodes:
        return None
    # Just in case there is more than one - shouldn't happen
    if len(nodes) > 1:
        raise ValueError('More than one node found for id %s: %s' % (id_, str(nodes)))
    return nodes[-1]


def get_node_properties(g, id_):
    """
        get the property dictionary of a graph node
    :param g:
    :param id_:
    :return:
    """
    # node = get_node(g, id_)
    # return g.V(node).valueMap().next()
    props = g.V(id_).propertyMap().next()
    # reduction of props to simple dict (abandoning VertexProperty class in favour of property value)
    props = {key: [e.value for e in props[key]] for key in props}
    # deflating lists
    return {key: props[key] if len(props[key]) > 1 else props[key][0] for key in props}


def expand_tree(tree_dict, g):
    """
        Given a tree with a single root node, return the simple dict corresponding to the tree
        If multiple roots are provided, they are treated as individual tree and the result is a list of dict trees

        The tree must be specified in a sequence of node-edge-node. Otherwise the behaviour is not predictable.

        expecting a gremlin tree of vertices/edges, for example:
        g.V(233).outE().inV().tree().next()
    """
    logging.debug('Expanding the tree and casting it into plain dict')
    if "@type" in tree_dict and "@value" in tree_dict:
        if not tree_dict["@value"]:
            # reached a leaf
            return None
        else:
            # iterate the tree nodes on 'key' and their children on 'value'
            expected_list_of_dicts = [expand_tree(kv, g) for kv in tree_dict["@value"]]

            # prime if the list of dicts are edges or nodes, nodes have '@id' and '@label' property while edges don't
            if expected_list_of_dicts and "@id" in expected_list_of_dicts[0]:
                # we have a list of node descriptions
                return expected_list_of_dicts
            else:
                # we have a list od edges, which need to be flattened because in the upper step they
                # are merged with the data properties of the node
                return flatten_list_of_dicts(expected_list_of_dicts)

    elif "key" in tree_dict and "value" in tree_dict:
        # process edge
        if isinstance(tree_dict["key"], Edge):
            return {tree_dict["key"].label: expand_tree(tree_dict["value"], g)}
        # process node (expand the node properties and merge with edges)
        elif isinstance(tree_dict["key"], Vertex):
            #             props = {k:(v[0].value if v[0] else None) for k,v in props}
            props = get_node_properties(g, tree_dict["key"])
            props["@id"] = tree_dict["key"].id
            props["@label"] = tree_dict["key"].label

            expected_dict_of_edge_props = expand_tree(tree_dict["value"], g)
            if expected_dict_of_edge_props:
                # deflating the values from lists to simple values if there is a single element provided
                expected_dict_of_edge_props = {
                    key: expected_dict_of_edge_props[key] if len(expected_dict_of_edge_props[key]) > 1 else
                    expected_dict_of_edge_props[key][0] for key in expected_dict_of_edge_props}
                # merge the two dictionaries, second overwriting the existing keys of the first one (Python3.5+)
                return {**props, **expected_dict_of_edge_props}
            else:
                return props


def get_nodes(g):
    """
        return all the nodes and their propoerties
    :param g:
    :return:
    """
    # g = setup_graph()
    return [{**node.__dict__, **properties} for node in g.V()
            for properties in g.V(node).valueMap()]


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


def get_edges(g, source_iri, target_iri):
    """
        retrieve the edges between source and target nodes identified by their URIs
    :param g: gremlin graph
    :param source_iri: source node URI
    :param target_iri: target node URI
    :return: the edge list
    """
    return g.V().has("iri", str(source_iri)).outE().as_("q").inV().has("iri", str(target_iri)).select("q").toList()
