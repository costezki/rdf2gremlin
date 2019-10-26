"""
setup
Date: 15.10.19
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

test_deps = [
    'coverage',
    'pytest',
    'pytest-cov',
]

extras = {
    'test': test_deps,
}

__version__ = "0.1.35"

setup(
    name="rdf2gremlin",
    version=__version__,
    install_requires=requirements,
    tests_require=test_deps,
    extras_require=extras,
    include_package_data=True,
    # package_data={'': ['*.txt'], },
    author="Eugeniu Costetchi",
    author_email="costezki.eugen@gmail.com",
    maintainer="Eugeniu Costetchi",
    maintainer_email="costezki.eugen@gmail.com",
    description="It has never been easier to transform your RDF data into a property graph based on TinkerPop-Gremlin.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/costezki/rdf2gremlin",
    platforms='any',
    keywords='RDF, Gremlin, load, tinkerpop, tinkerpop3, rdf-gremlin, serialisation, ',
    packages=find_packages(),  # exclude=["test", "test_*"]
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires='>=3.5',
)
