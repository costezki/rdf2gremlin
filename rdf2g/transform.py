"""
transform
Date: 19.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import logging
from functools import reduce
from rdf2g.retrieve import get_node_properties
from gremlin_python.structure.graph import Vertex, Edge


def expand_tree(g, tree_dict):
    """
        Given a tree, or a list of trees, with a single root node, return the simple dict corresponding to the tree
        If multiple roots are provided, they are treated as individual tree and the result is a list of dict trees.

        Note: The tree must be following node-edge-node sequence, otherwise the behaviour is not predictable.

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
            expected_list_of_dicts = [expand_tree(g, kv) for kv in tree_dict["@value"]]

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
            return {tree_dict["key"].label: expand_tree(g, tree_dict["value"])}
        # process node (expand the node properties and merge with edges)
        elif isinstance(tree_dict["key"], Vertex):
            #             props = {k:(v[0].value if v[0] else None) for k,v in props}
            props = get_node_properties(g, tree_dict["key"])
            props["@id"] = tree_dict["key"].id
            props["@label"] = tree_dict["key"].label

            expected_dict_of_edge_props = expand_tree(g, tree_dict["value"])
            if expected_dict_of_edge_props:
                # deflating the values from lists to simple values if there is a single element provided
                expected_dict_of_edge_props = {
                    key: expected_dict_of_edge_props[key] if len(expected_dict_of_edge_props[key]) > 1 else
                    expected_dict_of_edge_props[key][0] for key in expected_dict_of_edge_props}
                # merge the two dictionaries, second overwriting the existing keys of the first one (Python3.5+)
                return {**props, **expected_dict_of_edge_props}
            else:
                return props


def flatten_list_of_dicts(list_of_dicts):
    """
        Flatten the list of dictionaries:
        This is an expression for Python 3.5 or greater that merges dictionaries using reduce
        Warning: repeating keys will be overwritten.
    """
    return reduce(lambda x, y: {**x, **y}, list_of_dicts, {})
