"""
access
Date: 19.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""
import logging
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

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
        connection.close()
        connection = DriverRemoteConnection(conn_string, 'g')
        logging.debug('Connected')
        # The connection should be closed on shut down to close open connections with connection.close()
        g = graph.traversal().withRemote(connection)
        # Reuse 'g' across the application

        logging.info('Successfully connected to the graph server')
    except Exception as e:  # Shouldn't really be so broad
        logging.error("Could not connect to the Gremlin server. Run for example:" \
                      "\n'docker run --rm --name janusgraph-default janusgraph/janusgraph:latest' OR" \
                      "\n'docker run --name gremlin-server -p 8182:8182 tinkerpop/gremlin-server'")
        raise ConnectionError("Could not connect to the Gremlin server.")
    return g
