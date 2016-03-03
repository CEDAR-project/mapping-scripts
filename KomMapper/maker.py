#!/usr/bin/env python

# Exception maker for Koms; extremelly data dependent!
# TODO: stop copypasting code and make a generic script

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

# print cities

# Data structure
mappings = []

book = load("/Users/Albert/src/DataDump-mini-vt/source-data/VT_1859_01_H1.ods")
sheets = book.getElementsByType(Table)

for sheetIndex in range(0, len(sheets)):
    rows = sheets[sheetIndex].getElementsByType(TableRow)
    amco_str = unicode("0")
    for rowIndex in range(0, len(rows)):
        # Kom/buiten de kom is in column C
        try:
            kom = getColumns(rows[rowIndex])[2]
        except:
            continue
        lower_kom = unicode(kom).lower()
        if 'kom' in lower_kom:
            if 'totaal' in lower_kom:
                continue
            if 'buiten ' in lower_kom:
                mappings.append(['cell=VT_1859_01_H1-S%s-C%s' % (sheetIndex, rowIndex + 1), lower_kom, 'BuitenKom'])
            else:
                mappings.append(['cell=VT_1859_01_H1-S%s-C%s' % (sheetIndex, rowIndex + 1), lower_kom, 'BinnenKom'])

    with open('mappings.csv', 'wb') as csvfile:
        writer = UnicodeWriter(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['File name', 'Literal', 'Label', 'Code'])
        for mapping in mappings:
            writer.writerow(mapping)

exit(0)
