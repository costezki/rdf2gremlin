"""
retrieve
Date: 19.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import rdflib
from gremlin_python.process.graph_traversal import __
from gremlin_python.structure.graph import Vertex


def get_nodes(g):
    """
        return all the nodes and their properties
    :param g:
    :return:
    """
    return [{**node.__dict__, **properties} for node in g.V()
            for properties in g.V(node).valueMap()]


def get_node(g, id_):
    """
        return the node that is identified by id_
    :param g: gremlin graph
    :param id_: the node id or URI
    :return: the node
    """
    if isinstance(id_, (rdflib.URIRef, rdflib.BNode,)):
        nodes = g.V().has("iri", str(id_)).toList()
    elif isinstance(id_, str):
        nodes = g.V().hasLabel(id_).toList()
        if not nodes:
            nodes = g.V().has("iri", id_).toList()
    elif isinstance(id_, Vertex):
        return id_
    else:
        return g.V(id_).next()

    # If not found
    if not nodes:
        return []
    # Just in case there is more than one - shouldn't happen
    if len(nodes) > 1:
        raise ValueError('More than one node found for id %s: %s' % (id_, str(nodes)))
    return nodes[-1]


def get_edges(g, source_iri, target_iri):
    """
        retrieve the edges between source and target nodes identified by their URIs
    :param g: gremlin graph
    :param source_iri: source node URI
    :param target_iri: target node URI
    :return: the edge list
    """
    if source_iri:
        if target_iri:
            return g.V().has("iri", str(source_iri)).outE().as_("q").inV().has("iri", str(target_iri)).select(
                "q").toList()
        else:
            return g.V().has("iri", str(source_iri)).outE().toList()
    elif target_iri:
        return g.V().has("iri", str(target_iri)).inE().toList()
    return g.E().toList()


def get_node_properties(g, id_):
    """
        get the property dictionary of a graph node
    :param g: gremlin graph
    :param id_: node id
    :return:
    """
    props = g.V(id_).propertyMap().next()
    # reduction of props to simple dict (abandoning VertexProperty class in favour of property value)
    props = {key: [e.value for e in props[key]] for key in props}
    # deflating lists
    return {key: props[key] if len(props[key]) > 1 else props[key][0] for key in props}


def get_nodes_of_type(g, id_):
    """
        return nodes that have an link "rdf:type" to type node identified by id_
        :param g: gremlin graph
        :param id_: the type node label, URI, node id in the graph or gremlin Vertex object
    """
    type_id = get_node(g, id_)
    return g.V().as_("node").where(__.out("rdf:type").hasId(type_id.id)).select("node").dedup().toList()


def generate_traversal_tree(g, root_, max_depth=4):
    """
        generate the traversal tree in the graph starting from the selected root node down to max_depth iterations.

        the logic of the query is the following one:
            - traverse from node via an outgoing edge to another node, as incoming edge.
            - repeat this operation until either there are no more outgoing edges or
            - the maximum allowed repetitions was reached
            - remove duplicates and generate the tree

    :param g: gremlin graph
    :param root_: the graph node selected as starting point of the traversal
    :param max_depth: the maximum number of traversal hops
    :return: the traversal tree
    """
    node = get_node(g, root_)

    return g.V(node). \
        repeat(__.outE().inV().dedup()). \
        until(__.outE().count().is_(0).or_().loops().is_(max_depth)). \
        dedup().tree().next()
