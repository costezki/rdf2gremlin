"""
transform
Date: 19.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import logging
from functools import reduce
from pprint import pprint

from rdf2g.retrieve import get_node_properties
from gremlin_python.structure.graph import Vertex, Edge


def expand_tree(g, tree_dict) -> list:
    """
        Given a tree, or a list of trees, with a single root node, return the simple dict corresponding to the tree
        If multiple roots are provided, they are treated as individual tree and the result is a list of dict trees.

        Note: The tree must be following node-edge-node sequence, otherwise the behaviour is not predictable.

        expecting a gremlin tree of vertices/edges, for example:
        g.V(233).outE().inV().tree().next()

    :param g: the gremlin graph
    :param tree_dict: the traversal tree
    :return: list of nodes
    """
    # if it is a 'g:Tree' dict
    if "@type" in tree_dict and "@value" in tree_dict:
        if not tree_dict["@value"]:
            # a leaf is reached
            return None
        elif isinstance(tree_dict["@value"][0]["key"], Vertex):
            # deal with tree of vertices
            node_list = []
            for node in tree_dict["@value"]:
                prop_dict = get_node_properties(g, node["key"])
                edge_dict = expand_tree(g, node["value"])
                merged_dict = {**prop_dict, **edge_dict} if edge_dict else prop_dict  # expect only edge dict to be null
                node_list.append(merged_dict)
            return node_list
        elif isinstance(tree_dict["@value"][0]["key"], Edge):
            # deal with tree of edges
            edge_dict = {}
            for edge in tree_dict["@value"]:
                # consider having multiple usages of the same edge label
                edge_label = edge["key"].label
                if edge_label not in edge_dict:
                    edge_dict[edge_label] = []
                edge_dict[edge_label] += expand_tree(g, edge["value"])
            # deflate lists with single nodes
            edge_dict = {
                edge_label: node_list if len(node_list) > 1 else node_list[0]
                for edge_label, node_list in edge_dict.items()}
            return edge_dict
        else:
            raise IndexError("Unexpected structure! Expecting a list of dict and ['key', 'value'] in each dict keys.")
    else:
        raise IndexError("Unexpected structure! Expecting a dict and ['@type', '@value'] among the keys.")


def flatten_list_of_dicts(list_of_dicts):
    """
        Flatten the list of dictionaries:
        This is an expression for Python 3.5 or greater that merges dictionaries using reduce
        Warning: repeating keys will be overwritten.
    """
    return reduce(lambda x, y: {**x, **y}, list_of_dicts, {})
