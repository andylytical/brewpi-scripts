#!/usr/bin/env python3

import pathlib
import json
import re
import datetime

#import tabulate
#import pprint

#DATADIR = pathlib.Path( '.' )
DATADIR = pathlib.Path( '/var/www/html/data' )
COLS_REGEX = re.compile( 'Time|Temp|Set|SG' )


def html_start( title ):
    return '''
<html> <head>
<title>
''' + title + '''
</title>
<script type="text/javascript" src="dygraph.min.js"></script>
<link rel="stylesheet" src="dygraph.min.css" />
<style>
  #graphdiv {
    width: 640px;
    height: 480px;
    display: inline-block;
    vertical-align: top;
  }
  #legend {
    display: inline-block;
    vertical-align: top;
  }
</style>
</head>
<body> <h3>
''' + title + '''
</h3>
<div id="graphdiv"></div>
<div id="legend"></div>
<script type="text/javascript">
var tempFormat = function(y) {
    return parseFloat(y).toFixed(2);
};
var gravityFormat = function(y) {
    return parseFloat(y).toFixed(3);
};
'''

def html_end():
    return '</script> </body> </html>'


class jscode( object ):
    ''' A regular python string that will return without quotes when
        formatted with __repr__
    '''
    def __init__( self, rawstr ):
        self.line = rawstr

    def __str__( self ):
        return str( self.line )

    __repr__ = __str__


def get_jsonfiles():
    ''' Return a dict where key=brewdir and val=list of json filepaths
    '''
    data = {}
    for p in DATADIR.iterdir():
        if p.is_dir() and p.name != 'profiles':
            data[ p ] = []
            for f in p.iterdir():
                if f.is_file() and f.suffix == '.json':
                    data[ p ].append( f )
    return data


def j2py( elem, typ ):
    ''' Convert a json value into a native python datatype
    '''
    val = None
    if elem:
        rawval = elem[ 'v' ]
        if typ == 'datetime':
            val = jscode( 'new ' + rawval )
        elif typ == 'number':
            val = rawval
        elif typ == 'string':
            val = rawval
        else:
            raise UserWarning( "Unknown type '{}' from json".format( typ ) )
    return val


def py2js( val ):
    ''' Convert Python None type to javascript null type
    '''
    if isinstance( val, dict ):
        return { k: py2js( v ) for k,v in val.items() }
    elif isinstance( val, list ):
        return [ py2js( v ) for v in val ]
    if val is None:
        return jscode( 'null' )
    else:
        return val
        #raise UserWarning( f'Unhandled type for {val}' )


def filter_empty_cols( data ):
    ''' Remove columns of data in which there is no value present in any row.
        PARAMS:
            data - dict - of the form { 'headers': list,
                                        'rows': list of lists 
                                      }
        RETURN:
            cleandata - dict with same format as above but with empty cols removed
        Note: headers are excluded from checking for empty values,
              but will be filtered based on data from the remaining rows
    '''
    cols_with_data = []
    for ary in data[ 'rows' ]:
        for i, elem in enumerate( ary ):
            if elem is not None:
                cols_with_data.append( i )
    valid_cols = set( sorted( cols_with_data ) )
    cleanhdrs = [ data[ 'headers' ][ i ] for i in valid_cols ]
    cleanrows = []
    for ary in data[ 'rows' ]:
        cleanrows.append( [ ary[i] for i in valid_cols ] )
    return { 'headers': cleanhdrs, 'rows': cleanrows }



def parse_jsonfile( jpath ):
    with jpath.open() as fp:
        data = json.load( fp )
    col_nums = [ k for k,v in enumerate( data['cols'] ) if COLS_REGEX.search( v['id'] ) ]
    headers = [ data[ 'cols' ][ i ][ 'id' ] for i in col_nums ]
    rows = []
    for row in data[ 'rows' ]:
        values = []
        for i in col_nums:
            elem = row['c'][i]
            typ = data[ 'cols' ][ i ][ 'type' ]
            values.append( j2py( elem, typ ) )
        rows.append( values )
    return ( headers, rows )

def parse_jsondata( jsonlist ):
    ''' jsonlist is a dict where key=brewdir and val=list of json filepaths
        Returns list of rows, first row is headers, remaining rows are data
    '''
    brewdata = {}
    for brewdir, filelist in jsonlist.items():
        thisdata = { 'rows': [] }
        for jsonfile in sorted( filelist ):
#            print( f'Processing {jsonfile}' )
            hdrs, rows = parse_jsonfile( jsonfile )
            if 'headers' not in thisdata:
                thisdata[ 'headers' ] = hdrs
            if len( hdrs ) != len( thisdata[ 'headers' ] ):
                raise UserWarning( "mismatched headers in file: '{jsonfile}'" )
                raise UserWarning( "mismatched headers in file: '{}'".format( jsonfile ) )
#            print( f'Num rows: {len(rows)}' )
            thisdata[ 'rows' ].extend( rows )
        cleandata = filter_empty_cols( thisdata )
        brewdata[ brewdir ] = cleandata
    return brewdata


def mk_dygraph( data ):
    ''' data formated as: { 'headers': [...], 
                            'rows': [ [...], [...], ...  ] }
    '''
    color_map = { 'BeerTemp': 'rgb(41, 170, 41)',   #green
                  'BeerSet': 'rgb(240, 100, 100)',  #pink?
                  'FridgeTemp': 'rgb(89, 184, 255)', #light blue
                  'FridgeSet': 'rgb(255, 161, 76)',  #orange
                  'RoomTemp': 'rgb(153,0,153)',      #purple
                  'RedTemp': 'red',
                  'RedSG': 'red',
                  'GreenTemp': 'red',
                  'GreenSG': 'lime',
                  'BlackTemp': 'lime',
                  'BlackSG': 'black',
                  'PurpleTemp': 'purple',
                  'PurpleSG': 'purple',
                  'OrangeTemp': 'orange',
                  'OrangeSG': 'orange',
                  'BlueTemp': 'darkblue',
                  'BlueSG': 'darkblue',
                  'YellowTemp': 'yellow',
                  'YellowSG': 'yellow',
                  'PinkTemp':  'orchid',
                  'PinkSG': 'orchid',
}
    SG_details = { 'axis': 'y2', 'strokePattern': [ 7, 3 ] }
    SG_labels = [ 'RedSG', 'GreenSG', 'PurpleSG', 'BlackSG', 
                  'OrangeSG', 'BlueSG', 'YellowSG', 'PinkSG' ]
    series_opts = { k: SG_details for k in SG_labels }
    opts = {
        'legend': 'always',
        'labels': data[ 'headers' ],
        'colors': [ color_map[ k ] for k in data[ 'headers' ][ 1: ] ],
        'labelsDiv': jscode( "document.getElementById('legend')" ),
        'labelsSeparateLines': jscode( 'true' ),
        'series': series_opts,
        'ylabel': 'Temperature',
        'y2label': 'Gravity (SG)',
        'axes': { 
            'y': { 'valueFormatter': jscode( 'tempFormat' ),
                 },
            'y2': { 'valueRange': [ 0.990, jscode( 'null' ) ],
                    'valueFormatter': jscode( 'gravityFormat' ),
                    'axisLabelFormatter': jscode( 'gravityFormat' ),
                  },
        },
    }
    return '{}, {}, {} {}'.format(
        jscode( 'new Dygraph( document.getElementById("graphdiv")' ),
        data[ 'rows' ],
        opts,
        jscode( ');' ) )


def mk_html( title, data, outfile ):
    print( 'Writing file: {}'.format( outfile ) )
    with open( outfile.as_posix(), 'w' ) as fh:
        fh.writelines( [ html_start( title ), 
                         mk_dygraph( data ), 
                         html_end(),
                       ] )


def run():
    jsonlist = get_jsonfiles()
    brewdata = parse_jsondata( jsonlist )
    for dir, data in brewdata.items():
        print( 'Brewdir: '.format( dir ) )
#        print( tabulate.tabulate( data['rows'][0:10], headers=data['headers'] ) )
        #outfn = dir.parent.joinpath( dir.name ).with_suffix( '.html' )
        outfn = dir.parent.joinpath( dir.name ).with_suffix( '.html' )
        # convert python types to javascript where needed
        data = py2js( data )
        mk_html( dir.name, data, outfn )



if __name__ == '__main__':
    run()
