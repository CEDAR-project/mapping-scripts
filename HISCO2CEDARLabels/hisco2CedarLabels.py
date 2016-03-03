#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS
import json
import re

sparql = SPARQLWrapper("http://lod.cedar-project.nl:8080/sparql/cedar")

# Retrieve all HISCO URIs with their source observation PER YEAR
sparql.setQuery("""
PREFIX cedar: <http://cedar.example.org/ns#>
PREFIX cedardata: <http://cedar.example.org/resource/> 
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT DISTINCT ?hisco ?source
FROM <http://lod.cedar-project.nl/resource/r1/cedar-dataset> 
WHERE { GRAPH ?g {
?o cedar:occupation ?hisco .
?o cedar:sourceObservation ?source .
?o qb:dataSet cedardata:BRT-1930 .
}
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

hisco2SourceObservations = {}
sourceObservations2niceObservations = {}
niceObservations2Labels = {}

niceObservations = []

for result in results["results"]["bindings"]:
    hiscoURI = result["hisco"]["value"]
    sourceURI = result["source"]["value"]
    if hiscoURI not in hisco2SourceObservations:
        hisco2SourceObservations[hiscoURI] = []
    hisco2SourceObservations[hiscoURI].append(sourceURI)


# Replace all the funny broken URIs
for key, value in hisco2SourceObservations.iteritems():
    # Value is a list #justsaying
    for el in value:
        elSlice = el.split('/')
        fileName = elSlice[4]
        tableName = elSlice[5].split('_')[:-1]
        coords = elSlice[5].split('_')[-1]
        new = "http://www.data2semantics.org/data/" + str(fileName) + "/" + "_".join(tableName) + "/" + str(coords)
        sourceObservations2niceObservations[el] = new
        niceObservations.append(new)

# print(json.dumps(hisco2SourceObservations, indent=4))

query = """
PREFIX d2s: <http://www.data2semantics.org/core/>

SELECT ?s ?label
FROM <http://lod.cedar-project.nl/resource/v2/cedar-dataset>
WHERE { GRAPH ?g {
?s d2s:isObservation ?o .
?o ?prop ?occ .
?occ skos:prefLabel ?label .
FILTER regex(?prop, "Beroep", "i")
FILTER regex(?s, "BRT_1930", "i")
}
}
"""

sparql.setQuery(query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    obsURI = result["s"]["value"]
    label = result["label"]["value"]
    niceObservations2Labels[obsURI] = label

# print(json.dumps(niceObservations2Labels, indent=4))

hisco2labels = {}
for k, v in hisco2SourceObservations.iteritems():
    hisco2labels[k] = []
    for dirty in v:
        niceObs = sourceObservations2niceObservations[dirty]
        if niceObs in niceObservations2Labels:
            hisco2labels[k].append(niceObservations2Labels[niceObs])

# print(json.dumps(hisco2SourceObservations, indent=4))
# print(json.dumps(sourceObservations2niceObservations, indent=4))
# print(json.dumps(niceObservations2Labels, indent=4))

g = Graph()
for k, v in hisco2labels.iteritems():
    for label in v:
        g.add( (URIRef(k), SKOS.prefLabel, Literal(label)) )

g.serialize('out.nt', format='nt')
