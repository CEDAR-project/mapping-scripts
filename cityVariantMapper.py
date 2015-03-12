#!/usr/bin/env python

import csv
import logging
import sys
import distance

cities = {}
cities_to_map = []
mappings = {}

logging.basicConfig(level=logging.DEBUG)
logging.info('Starting cityVariantMapper')

logging.info('Loading reference data...')
with open('cities.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        cities[row[0]] = row[1]

logging.info('Loading data to map...')
with open('cities_variants.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        cities_to_map.append(row[0])

logging.info('Finding mappings...')
for c1 in cities_to_map:
    c1_norm = c1.split('(')[0].strip().lower()
    min_distance = sys.maxint
    best_match = cities.keys()[0]
    for c2 in cities.keys():
        d = distance.nlevenshtein(c1_norm, c2) 
        if d < min_distance:
            min_distance = d
            best_match = c2
    mappings[c1] = [best_match, min_distance]
#    logging.info('Best match for %s is %s with distance %s' % (c1, best_match, min_distance) )

logging.info('Serializing similarity table...')
with open('similarities.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for key, value in mappings.iteritems():
        writer.writerow([key, value[0], value[1]])

logging.info('Serializing AMCO mapping table...')
with open('mappings.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for key, value in mappings.iteritems():
        writer.writerow([key, cities[value[0]]])

logging.info('Done.')
