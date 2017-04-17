#!/usr/bin/env python3

import pathlib
import json
import re
import datetime
import string
import urllib

#import tabulate
#import pprint

DATADIR = pathlib.Path( '/var/www/html/data' )
#COLS_REGEX = re.compile( 'Time|Temp|Set|SG' )
COLS_REGEX = re.compile( 'Time|BeerTemp|BeerSet|SG' )
COLOR_MAP = { 'BeerTemp': 'rgb(41, 170, 41)',   #green
              'BeerSet': 'rgb(240, 100, 100)',  #pink?
              'FridgeTemp': 'rgb(89, 184, 255)', #light blue
              'FridgeSet': 'rgb(255, 161, 76)',  #orange
#              'RoomTemp': 'rgb(153,0,153)',      #purple
              'RoomTemp': 'rgb(128,128,128)',     #grey
              'RedTemp': 'red',
              'RedSG': 'red',
              'GreenTemp': 'lime',
              'GreenSG': 'lime',
              'BlackTemp': 'black',
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


class myTemplate( string.Template ):
    delimiter = '___'


class jscode( object ):
    ''' A regular python string that will return without quotes when
        formatted with __repr__
    '''
    def __init__( self, rawstr ):
        self.line = rawstr

    def __str__( self ):
        return str( self.line )

    __repr__ = __str__


def safe_filename( rawfn ):
    return urllib.parse.unquote_plus( rawfn )


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
            data - dict - of the form { 'labels': list,
                                        'values': list of lists 
                                      }
        RETURN:
            cleandata - dict with same format as above but with empty cols removed
        Note: labels are excluded from checking for empty values,
              but will be filtered based on data from the remaining values (rows)
    '''
    cols_with_data = []
    for ary in data[ 'values' ]:
        for i, elem in enumerate( ary ):
            if elem is not None:
                cols_with_data.append( i )
    valid_cols = set( sorted( cols_with_data ) )
    cleanhdrs = [ data[ 'labels' ][ i ] for i in valid_cols ]
    cleanrows = []
    for ary in data[ 'values' ]:
        cleanrows.append( [ ary[i] for i in valid_cols ] )
    return { 'labels': cleanhdrs, 'values': cleanrows }



def parse_jsonfile( jpath ):
    with jpath.open() as fp:
        data = json.load( fp )
    col_nums = [ k for k,v in enumerate( data['cols'] ) if COLS_REGEX.search( v['id'] ) ]
    labels = [ data[ 'cols' ][ i ][ 'id' ] for i in col_nums ]
    rows = []
    for row in data[ 'rows' ]:
        values = []
        for i in col_nums:
            elem = row['c'][i]
            typ = data[ 'cols' ][ i ][ 'type' ]
            values.append( j2py( elem, typ ) )
        rows.append( values )
    return ( labels, rows )

def parse_jsondata( jsonlist ):
    ''' jsonlist is a dict where key=brewdir and val=list of json filepaths
        Returns list of rows, first row is labels, remaining rows are data
    '''
    brewdata = {}
    for brewdir, filelist in jsonlist.items():
        thisdata = { 'values': [] }
        for jsonfile in sorted( filelist ):
#            print( f'Processing {jsonfile}' )
            hdrs, rows = parse_jsonfile( jsonfile )
            if 'labels' not in thisdata:
                thisdata[ 'labels' ] = hdrs
            if len( hdrs ) != len( thisdata[ 'labels' ] ):
                raise UserWarning( "mismatched labels in file: '{}'".format( jsonfile ) )
#            print( f'Num rows: {len(rows)}' )
            thisdata[ 'values' ].extend( rows )
        cleandata = filter_empty_cols( thisdata )
        brewdata[ brewdir ] = cleandata
#        brewdata[ brewdir ] = thisdata
    return brewdata


def mk_dygraph( data ):
    ''' data formated as: { 'labels': [...], 
                            'values': [ [...], [...], ...  ] }
    '''
    global COLOR_MAP
    SG_details = { 'axis': 'y2', 'strokePattern': [ 7, 3 ] }
    SG_labels = [ 'RedSG', 'GreenSG', 'PurpleSG', 'BlackSG', 
                  'OrangeSG', 'BlueSG', 'YellowSG', 'PinkSG' ]
    series_opts = { k: SG_details for k in SG_labels }
    opts = {
        'legend': 'always',
        'labels': data[ 'labels' ],
        'colors': [ COLOR_MAP[ k ] for k in data[ 'labels' ][ 1: ] ],
        'labelsDiv': jscode( "document.getElementById('curr-beer-chart-label')" ),
        'labelsSeparateLines': jscode( 'true' ),
        'series': series_opts,
        'ylabel': jscode( "'Temperature (' + window.tempFormat + ')'" ),
        'y2label': 'Gravity (SG)',
        'axes': { 
#            'y': { 'valueFormatter': jscode( 'tempFormatr' ),
#                 },
            'y2': { 'valueRange': [ 0.990, jscode( 'null' ) ],
#                    'valueFormatter': jscode( 'gravityFormat' ),
                    'axisLabelFormatter': jscode( 'gravityFormat' ),
                  },
        },
        'highlightCircleSize': 2,
        'highlightSeriesOpts': {
            'strokeWidth': 1.5,
            'strokeBorderWidth': 1,
            'highlightCircleSize': 5,
        },
#        'highlightCallback': 
#            jscode( 'function(e, x, pts, row) { showChartLegend(e, x, pts, row, beerChart); }' ),
#        'unhighlightCallback': 
#            jscode( 'function(e) { hideChartLegend(); }' ),
    }
    beer_chart = '{},\n{},\n{}\n{}'.format( 
        jscode( 'var beerChart = new Dygraph( document.getElementById("curr-beer-chart")' ),
        data[ 'values' ],
        opts,
        jscode( ');' )
        )
    return beer_chart


def mk_legend_rows( data ):
    ''' data formated as: { 'labels': [...], 
                            'values': [ [...], [...], ...  ] }
    '''
    label_template = ( ''
        '<div class="beer-chart-legend-row ___LABEL">'
        '    <div class="toggle ___LABEL" onClick="toggleLine(this)"></div>'
        '    <div class="beer-chart-legend-label" onClick="toggleLine(this)">___LABEL</div>'
        '    <div class="beer-chart-legend-value">--</div>'
        '    <br class="crystal" />'
        '</div>' )
    row_tmpl = myTemplate( label_template )
    rows = []
    for label in data[ 'labels' ][ 1: ]:
        rows.append( row_tmpl.substitute( { 'LABEL': label } ) )
    return '\n'.join( rows )
    


def mk_html( template_data, outfile ):
    with open( 'brewlog.html.tmpl' ) as infile:
        doc = infile.read()
    tmpl = myTemplate( doc )
    print( 'Writing file: {}'.format( outfile ) )
    with open( outfile.as_posix(), 'w' ) as fh:
        fh.write( tmpl.substitute( template_data ) )


def run():
    jsonlist = get_jsonfiles()
    brewdata = parse_jsondata( jsonlist )
    for dir, data in brewdata.items():
        print( 'Brewdir: '.format( dir ) )
#        print( tabulate.tabulate( data['rows'][0:10], labels=data['labels'] ) )
        outfn = dir.parent.joinpath( dir.name ).with_suffix( '.html' )
        # convert python types to javascript where needed
        data = py2js( data )
        template_data = { 'BEERNAME': safe_filename( dir.name ),
                          'BEERCHART': mk_dygraph( data ),
#                          'BEERCHARTLEGEND': mk_legend_rows( data ),
                          'BEERCHARTLEGEND': '',
                        }
        mk_html( template_data, outfn )



if __name__ == '__main__':
    run()
