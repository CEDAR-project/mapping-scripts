#!/usr/bin/env python

# Exception maker for 1909; extremelly data dependent!

from odf.opendocument import load
from odf.table import Table, TableRow
from odf.namespaces import TABLENS, STYLENS
from xlrd import open_workbook
from xlutils.margins import number_of_good_cols, number_of_good_rows
import csv
import cStringIO
import codecs
import sys
import distance

# Aux nasty func

def getColumns(row):
    columns = []
    node = row.firstChild
    end = row.lastChild
    while node != end:
        (_, t) = node.qname
        
        # Focus on (covered) table cells only
        if t != 'covered-table-cell' and t != 'table-cell':
            continue
        
        # If the cell is covered insert a None, otherwise use the cell
        n = node if t == 'table-cell' else None
        columns.append(n)
        
        # Shall we repeat this ?
        repeat = node.getAttrNS(TABLENS, 'number-columns-repeated')
        if repeat != None:
            repeat = int(repeat) - 1
            while repeat != 0:
                columns.append(n)
                repeat = repeat - 1
        
        # Move to next node
        node = node.nextSibling
    return columns

# Best match Levenstein func

def bestMatch(label, candidates, T=0.266666667):
    min_distance = sys.maxint
    best_match = candidates[0]
    for c in candidates:
        d = distance.nlevenshtein(label, c) 
        if d < min_distance:
            min_distance = d
            best_match = c
    if min_distance <= T:
        return best_match
    else:
        return -1

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        '''writerow(unicode) -> None
        This function takes a Unicode string and encodes it to the output.
        '''
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

cities = {}

wb = open_workbook("/Users/Albert/src/DataDump/mapping/Cities.xls", formatting_info=False, on_demand=True)
sheet = wb.sheet_by_index(0)
colns = number_of_good_cols(sheet)
rowns = number_of_good_rows(sheet)
for i in range(1, rowns):
    cities[sheet.cell(i,1).value] = int(sheet.cell(i,2).value)

# print cities

# Data structure
mappings = []

book = load("/Users/Albert/src/DataDump/source-data/VT_1909_01_T.ods")
sheets = book.getElementsByType(Table)

rows = sheets[0].getElementsByType(TableRow)
amco = 0
amco_str = unicode("0")
for rowIndex in range(8, 13288):
    current = unicode(getColumns(rows[rowIndex])[0])
    current_lower = unicode(getColumns(rows[rowIndex])[0]).split('(')[0].lower()
    if 'totaal' in current_lower:
        mappings.append(["cell=VT_1909_01_T-S0-A%s" % (rowIndex + 1), current, amco_str, unicode(amco)])
        amco = 0
        amco_str = unicode("0")
        continue
    if amco_str == unicode("0"):
        best_match = bestMatch(current_lower, cities.keys())
        if best_match in cities:
            # Row matches city name - update amco
            amco = cities[best_match]
            amco_str = best_match
    mappings.append(["cell=VT_1909_01_T-S0-A%s" % (rowIndex + 1), current, amco_str, unicode(amco)])

with open('mappings.csv', 'wb') as csvfile:
    writer = UnicodeWriter(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['File name', 'Literal', 'Label', 'Code'])
    for mapping in mappings:
        writer.writerow(mapping)

exit(0)
