"""
__init__.py
Date: 13.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import logging
from rdf2g.operations import *

__version__ = "0.1.3"

level = logging.INFO

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    level=level)
logging.getLogger().setLevel(level)
