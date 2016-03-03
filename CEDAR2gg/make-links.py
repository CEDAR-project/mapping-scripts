#!/usr/bin/env python

from rdflib import URIRef, Graph
from SPARQLWrapper import SPARQLWrapper, JSON

ggNamespace = URIRef("http://www.gemeentegeschiedenis.nl/amco/rdfxml/")
linkPredicate = URIRef("http://www.w3.org/2002/07/owl#sameAs")
outFile = 'cedar2gg-links.ttl'
outFormat = 'turtle'

g = Graph()

sparql = SPARQLWrapper("http://lod.cedar-project.nl:8080/sparql/cedar")
sparql.setQuery("""
prefix qb: <http://purl.org/linked-data/cube#>
prefix cedar: <http://cedar.example.org/ns#>

select distinct ?city from <http://lod.cedar-project.nl/resource/r1/cedar-dataset> where {
graph ?g {
?o cedar:city ?city .
}}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    cityURI = URIRef(result["city"]['value'])
    # Get the AMCO from the URI
    amco = cityURI.split('-')[-1]
    # Generate the gemeentegeschiedenis.nl URIs
    ggURI = URIRef(ggNamespace + amco)
    g.add((cityURI, linkPredicate, ggURI))

g.serialize(outFile, outFormat)
print "Serialized %s links" % str(len(g))
