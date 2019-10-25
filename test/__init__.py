"""
__init__.py
Date: 13.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""
import pathlib

OUTPUT_FILE_LAM_PROPERTIES = (
            pathlib.Path(__file__).resolve().parent.parent / "resource/celex_project_properties_v2.ttl").resolve()

CONCEPT_SCHEME_QNAME = "skos:ConceptScheme"
CONCEPT_QNAME = "skos:Concept"