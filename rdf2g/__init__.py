"""
__init__.py
Date: 13.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

from rdf2g.update import *
from rdf2g.access import *
from rdf2g.retrieve import *
from rdf2g.transform import *

import logging
import rdflib
from gremlin_python import statics
from gremlin_python.structure.graph import Graph, Vertex, Edge, Element
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import T, P, Operator, Bindings
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

level = logging.INFO

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    level=level)
logging.getLogger().setLevel(level)
