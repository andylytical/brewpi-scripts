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


jfile = get_json_file()
print( "\n{0}\n".format( os.path.basename( jfile ) ) )

with open( jfile ) as fh:
    data = json.load( fh )

rex = re.compile( 'Time|BeerTemp|FridgeTemp|RoomTemp|RedTemp|RedSG' )
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
    #datalist = [ row['c'][i]['v'] for i in col_nums ]
    rows.append( values )

print( tabulate.tabulate( rows, headers=headers ) )
