# rdf2gremlin
It has never been easier to transform your RDF data into a property graph based on TinkerPop-Gremlin.

# Introduction
[Apache TinkerPop](<http://tinkerpop.apache.org>) is a graph computing framework for both graph databases (OLTP) and graph analytic systems (OLAP). [Gremlin](<http://tinkerpop.apache.org/gremlin.html>) is the graph traversal language of TinkerPop.

The [Resource Description Framework (RDF)]() is a standard model for data interchange on the Web originally designed as a metadata data model. It has come to be used as a general method for conceptual description or modeling of information that is implemented in web resources, using a variety of syntax notations and data serialization formats. This linking structure forms a *directed labeled graph*, where the *edges* represent the named link between two resources, represented by the *graph nodes*. This graph view is the easiest possible mental model for RDF and is often used in easy-to-understand visual explanations. Resources are denoted by IRIs. The general convention is to use *http* URIs. 

RDF graphs are queries using SPARQL language. [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/) is a set of specifications that provide languages and protocols to query and manipulate RDF graph content on the Web or in an RDF store.    

This library, [rdf2gremlin](https://github.com/costezki/rdf2gremlin), provides an easy way to load the RDF data-sets into a property graph in order to benefit from the features of traversal language, which are not available in SPARQL pattern matching language. 

# Installation

```shell script
# switch to your local virtual environment 
. ./venv/activate

pip install rdf2gremlin
# ... enjoy ...
```

# Prerequisites

Gremlin-Python is designed to connect to a "server" that is hosting a TinkerPop-enabled graph system. That "server"
could be [Gremlin Server](http://tinkerpop.apache.org/docs/current/reference/#gremlin-server) or a [remote Gremlin provider](http://tinkerpop.apache.org/docs/current/reference/#connecting-rgp) that exposes protocols by which Gremlin-Python can connect. This requirement is inherited by the current library as well. 

In order to use this library it is necessary to have a Gremlin service available locally or on a remote location. The easiest way is to run a TinkerProp server locally. This can be done by either: 
(a) downloading and running TinkerPop 
 ```shell script
wget https://www-eu.apache.org/dist/tinkerpop/3.4.3/apache-tinkerpop-gremlin-server-3.4.3-bin.zip
unzip apache-tinkerpop-gremlin-server-3.4.3-bin.zip
cd apache-tinkerpop-gremlin-server-3.4.3/
./bin/gremlin-server.sh start
 
# ... to stop the server ...

./bin/gremlin-server.sh stop
```
or (b) running it as a Docker container.
```shell script
docker pull tinkerpop/gremlin-server
docker run --name gremlin-server -p 8182:8182 tinkerpop/gremlin-server

# ... to stop the server ...

docker stop gremlin-server
```

# Getting started

### Connect to a property graph service.
A typical connection to a server running on "localhost" that supports the Gremlin Server protocol using websockets from the Python shell looks like this:

```python
from rdf2g import setup_graph

DEFAULT_LOCAL_CONNECTION_STRING = "ws://localhost:8182/gremlin"
g = setup_graph(DEFAULT_LOCAL_CONNECTION_STRING)
```
Once `g` has been created using a connection, it is then possible to start writing Gremlin traversals to query the remote graph. 

### Load a graph

Read an RDF graph.

```python
import rdflib
import pathlib

OUTPUT_FILE_LAM_PROPERTIES = pathlib.Path("../resource/celex_project_properties_v2.ttl").resolve()

rdf_graph = rdflib.Graph()
rdf_graph.parse(str(OUTPUT_FILE_LAM_PROPERTIES), format="ttl")
``` 

Load the RDF graph into a property graph.

```python
from rdf2g import load_rdf2g
load_rdf2g(g, rdf_graph)
```

The created property graph follows the following set of **conventions**.

* URIs and Blank nodes are transformed into property graph nodes.
* Predicates connecting an URI to another URI or a blank node are transformed into property graph edges. Edge labels correspond to qualified IRIs generated using the prefix definitions available in the RDF data-set.
* Node labels correspond to qualified IRIs generated using the prefix definitions available in the RDF data-set.  
* RDF Litarals are transformed into values of the node properties, while the preceding predicates into keys of the node properties. In other words
* Predicates connecting an URI to a RDF Literal are transformed into {key:value} pairs and added as node properties.  
* Nodes have a special property 'iri' that is equivalent to the absolute URI of the RDF resource.
 
### Generate a traversal tree 

It is possible to traverse the property graph and then generate the traversal tree from it. This is especially useful when the graph serves as structured document content say JSON or XML serialisation.      

To do that first, get two levels deep traversal tree and the edges between them for all the nodes in the graph that have `iri == known_iri`. Further please see the [Gremlin reference documentation](http://tinkerpop.apache.org/docs/current/reference/#gremlin-python) at Apache TinkerPop for more information on usage.

```python
known_iri = 'http://publications.europa.eu/resources/authority/celex/md_CODE' 
s = g.V().has('iri', known_iri).outE().inV().tree().next()
```

Then expand and simplify that tree. First, simplify the dict structure to simple Python types, removing the Gremlin objects. Second, expand by providing the properties for each visited node, while the edges are considered as special properties leading to a another node dictionary.

```python
from rdf2g import expand_tree
from pprint import pprint
result = expand_tree(s, g)
pprint (result)
```

The traversal tree nodes contain, in addition to original RDF content, two special properties `@id` and `@label` which correspond to the standard Gremlin `id` and `label` properties. The `@` sign is used to distinguish the original RDF from the Gremlin features. Property graph edges, are reduced to keys in the final dict and for this reason they have no additional descriptions just like in the original RDF graph.

# Contributing
You are more than welcome to help expand and mature this project. 

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

# License

This project is Licensed under the GPL v3 License - see [LICENSE](LICENSE) file
