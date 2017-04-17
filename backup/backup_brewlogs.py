#!/usr/bin/python3

import logging
import pprint
import pathlib
import os
import urllib
import subprocess
import shutil



WWW = pathlib.Path( '/var/www/html' )
HOME = pathlib.Path( os.environ['HOME'] )
DBUL = str( HOME/'Dropbox-Uploader/dropbox_uploader.sh' )

def backup_beer_logs():
    tgtbase = pathlib.Path( '/' )
    sync_dir_to_DB( WWW/'data', tgtbase )
    sync_dir_to_DB( WWW/'css', tgtbase/'css', base=WWW )
    sync_dir_to_DB( WWW/'js', tgtbase/'js', base=WWW )
    sync_dir_to_DB( WWW/'font', tgtbase/'font', base=WWW )
    sync_file_to_DB( WWW/'brewpi_logo.png', tgtbase/'brewpi_logo.png' )
#    sync_file_to_DB( HOME/'brewpi-scripts/backup/brewlog.js', tgtbase/'brewlog.js' )


def safe_filename( rawfn ):
    return urllib.parse.unquote_plus( rawfn )


def DB_list_or_make_dir( safepath ):
    ''' safepath should start with a /
    '''
    raw_list = ''
    contents = { 'DIRS': {}, 'FILES': {} }
    dir_exists = False
    try:
        raw_list = runcmd( DBUL, args=[ '-q', 'list', safepath ] )
    except ( Run_Cmd_Error ) as e:
        # Error code == 1 might just be that the directory doesn't exist
        # Error code other than 1 is a problem
        if e.code > 1:
            raise e
        logging.debug( "Attempt to list remote dir '{}' failed.".format( safepath ) )
    else:
        dir_exists = True
    # Confirm if e.code==1 (from above) is simply that remote dir doesn't exist yet
    if not dir_exists:
        logging.debug( "Checking parent dir '{}' for existance".format( safepath.parent ) )
        runcmd( DBUL, args=[ '-q', 'list', safepath.parent ] )
        # parent exists and listed okay (otherwise an exception would have been raised)
        # just create the remote dir
        logging.debug( "Parent OK" )
        logging.info( "mkdir( {} ).".format( safepath ) )
        runcmd( DBUL, args=[ '-q', 'mkdir', safepath ] )
    for line in raw_list.splitlines():
        logging.debug( "Processing line:\n{}".format( line ) )
        line = line.strip()
        parts = line.split( maxsplit=1 )
        key = 'DIRS'
        size = 0
        if line.startswith( '[F]' ):
            parts = line.split( maxsplit=2 )
            key = 'FILES'
            size = int( parts[1] )
        path = pathlib.Path( safepath ) / parts[-1]
        contents[ key ][ path ] = size
    return contents


def sync_dir_to_DB( src, tgt, base=None ):
    safe_tgt = pathlib.Path( safe_filename( str( tgt ) ) )
    remote_contents = DB_list_or_make_dir( safe_tgt )
    logging.debug( 'Remote Contents:\n{}'.format( pprint.pformat( remote_contents ) ) )
    if not base:
        base = src
    dirs = []
    # cycle through local dir contents, check they exist on the remote side
    for p in src.iterdir():
        if p.is_dir():
            # save dirs for later recursing
            dirs.append( p )
            logging.debug( 'Found localdir: {}'.format( p ) )
            continue
        if p.is_file():
            logging.debug( 'Found localfile: {}'.format( p ) )
            # construct equivalent target
            start = len( base.parts )
            new_path = '/' + '/'.join( p.parts[ start : ] )
            remote_p = pathlib.Path( safe_filename( new_path ) )
            logging.debug( 'Remote filepath: {}'.format( pprint.pformat( remote_p ) ) )
            target_needs_update = False
            try:
                remote_size = remote_contents[ 'FILES' ][ remote_p ]
            except ( KeyError ) as e:
                # remote file doesn't exist, flag for update
                target_needs_update = True
            else:
                # file exists on remote, compare size
                logging.debug( 'Found remote match, comparing sizes...' )
                local_size = p.stat().st_size
                logging.debug( 'Local file size: {}'.format( local_size ) )
                if local_size != remote_size:
                    target_needs_update = True
                else:
                    logging.debug( 'Sizes match, no update needed' )
            if target_needs_update:
                sync_file_to_DB( p, remote_p )
    for d in dirs:
        #TODO : implement and test recursion for entire tree
        sync_dir_to_DB( d, tgt / d.name, base=base )
        #logging.warning( 'Recursion into dirs not complete, skipping {}'.format( d ) )

def sync_file_to_DB( src, tgt ):
    logging.info( '\n{} >>>> {}'.format( src, tgt ) )
    # Have to copy src file to a safename that dropbox uploader can work with
    tmp = pathlib.Path( '/tmp/brewpibkuptmpfn' )
    logging.debug( 'tmp: {}'.format( tmp ) )
    shutil.copy( str( src ), str( tmp ) )
    runcmd( DBUL, args=[ '-q', 'upload', tmp, tgt ] )


def run():
    backup_beer_logs()


def runcmd( cmdname, opts=None, args=None ):
    cmdlist = [ cmdname ]
    if opts:
        cmdlist.extend( [ "{0}={1}".format( k, v ) for k, v in opts.items() ] )
    if args:
        cmdlist.extend( map( str, args ) )
    logging.debug( "cmdlist: {0}".format( cmdlist ) )
    subp = subprocess.Popen( cmdlist, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE )
    ( output, errput ) = subp.communicate()
    rc = subp.returncode
    if rc != 0:
        raise( Run_Cmd_Error( code=rc, reason=errput ) )
    return output.decode( 'utf-8' )


class Run_Cmd_Error( Exception ):
    def __init__( self, code, reason, *a, **k ):
        super( Run_Cmd_Error, self ).__init__( *a, **k )
        self.code = code
        self.reason = reason

    def __str__( self ):
        return "<{0} (code={1} msg={2})>".format(
            self.__class__.__name__, self.code, self.reason )



if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s-%(filename)s[%(lineno)d]-%(funcName)s-%(message)s"
        )
    run()
