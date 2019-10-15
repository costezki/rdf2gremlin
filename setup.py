"""
setup
Date: 15.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""
from setuptools import setup, find_packages
import rdf2g

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="rdf2gremlin",
    version=rdf2g.__version__,
    install_requires=requirements,
    author="Eugeniu Costetchi",
    author_email="costezki.eugen@gmail.com",
    description="It has never been easier to transform your RDF data into a property graph based on TinkerPop-Gremlin.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/costezki/rdf2gremlin",
    platforms='any',
    keywords='RDF, Gremlin, load, tinkerpop, tinkerpop3, rdf-gremlin, serialisation, ',
    packages=find_packages(exclude=["test", "test_*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.5',
)
