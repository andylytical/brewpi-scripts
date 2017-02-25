#!/usr/bin/python

import os
import os.path
import json
import re
import tabulate


def get_json_file():
    dir='/var/www/html/data'
    json_list = []
    for root, dirs, files in os.walk( dir ):
        for f in files:
            if f.endswith( '.json' ):
	        json_list.append( os.path.join( root, f ) )
    sorted_list = sorted( json_list, key=os.path.getmtime )
    return sorted_list[-1]


###
#  Remove columns of data in which there is no value present in any row
#  PARAMS:
#    rows - list of lists, assume first row is headers
#           Note: headers are excluded from checking for empty values, 
#                 but will be filtered based on data from the remaining rows
###
def filter_empty_cols( rows ):
    cols_with_data = []
    for ary in rows[1:]:
        for i, elem in enumerate( ary ):
            if elem is not None:
                cols_with_data.append( i )
    valid_cols = set( sorted( cols_with_data ) )
    cleanrows = []
    for ary in rows:
        newrow = []
        for i in valid_cols:
            newrow.append( ary[i] )
        cleanrows.append( newrow )
    return cleanrows


jfile = get_json_file()
print( "\n{0}\n".format( os.path.basename( jfile ) ) )

with open( jfile ) as fh:
    data = json.load( fh )

rex = re.compile( 'Time|Temp|SG' )
col_nums = []
for k,v in enumerate( data[ 'cols' ] ):
    name = v['id']
    if rex.search( name ):
        col_nums.append( k )

headers = [ data['cols'][i]['id'] for i in col_nums ]

rows = []
for row in data['rows']:
    values = []
    for i in col_nums:
        elem = row['c'][i]
        val = None
        if elem is not None:
            val = elem['v']
        values.append( val )
    rows.append( values )

filtered_rows = filter_empty_cols( [ headers ] + rows )

print( tabulate.tabulate( filtered_rows, headers="firstrow" ) )
