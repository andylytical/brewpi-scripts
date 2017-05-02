#!/usr/bin/python3

#TODO - Replace Dropbox-Uploader with DropBox Official Python API
#       https://www.dropbox.com/developers/documentation/python

import logging
import pprint
import pathlib
import os
import urllib
import dropbox
import time
import datetime



class Dropbox_Sync( object ):

    def __init__( self ):
        self.dbx = self.dbx_init()


    def dbx_init( self ):
        env_home = pathlib.Path( os.environ['HOME'] )
        tokenfile = env_home/'.dropbox_token'
        with tokenfile.open() as fh:
            lines = fh.readlines()
        token = lines[0].strip()
        return dropbox.Dropbox( token )


    def list_or_make_dir( self, remote_path ):
        ''' If remote_path exists, list contents
            Else, create remote_path and return empty list
            INPUT:
                remote_path - pathlib.Path
        '''
        contents = {}
        dir_exists = True
        # if remote_path is base (ie: '/'), replace with empty string
        lookup_str = str( remote_path )
        if remote_path.match( '/' ):
            lookup_str = ''
        try:
            results = self.dbx.files_list_folder( lookup_str )
        except ( dropbox.exceptions.ApiError ) as e :
            dberr = e.error
            if dberr.is_path():
                lookup_err = dberr.get_path()
                if lookup_err.is_not_found():
                    dir_exists = False
                    logging.debug( "remote dir '{}' does not exist".format( remote_path ) )
                else:
                    raise e
            else:
                raise e
        if not dir_exists:
            logging.debug( "Attempt to create remote_dir '{}'".format( remote_path ) )
            # create the remote dir
            res = self.dbx.files_create_folder( lookup_str )
            logging.info( "Create folder success: '{}'".format( res.path_display ) )
        else:
            for entry in results.entries:
                #contents[ pathlib.Path( entry.name ) ] = entry
                contents[ entry.name ] = entry
        return contents


    def sync_dir( self, local_dir, remote_dir ):
        ''' Recursively sync local_dir to remote_dir
            INPUT:
                local_dir - pathlib.Path
                remote_dir - pathlib.Path
        '''
        remote_contents = self.list_or_make_dir( remote_dir )
#        logging.debug( 'Remote contents:\n{}'.format( pprint.pformat( remote_contents ) ) )
        dirs = []
        # cycle through local dir contents, check they exist on the remote side
        for src_path in local_dir.iterdir():
            if src_path.is_file():
#                logging.debug( 'Found localfile: {}'.format( src_path ) )
                tgt_meta = None
                if src_path.name in remote_contents:
                    # remote file exists
                    tgt_meta = remote_contents[ src_path.name ]
                self.sync_file( src_path, 
                                remote_dir/src_path.name, 
                                tgt_meta = tgt_meta )
            if src_path.is_dir():
                # save dirs for later
                dirs.append( src_path )
#                logging.debug( 'Found localdir: {}'.format( src_path ) )
                continue
        for d in dirs:
            self.sync_dir( d, remote_dir/d.name )


    def sync_file( self, src, tgt, tgt_meta=None ):
        ''' If tgt_meta is not provided, attempt to retrieve metadata from Dropbox.
            Compare size and mtime for src and tgt. Upload if file is not in sync
            OR if tgt file does not exist yet.
            Do nothing otherwise.
            INPUT:
                src - pathlib.Path
                tgt - pathlib.Path
                tgt_meta - dropbox.files.Metadata
        '''
        tgt_needs_update = True
        if tgt_meta is None:
            try:
                tgt_meta = self.dbx.files_get_metadata( tgt.as_posix() )
            except ( dropbox.exceptions.ApiError ) as e:
                dberr = e.error
                if dberr.is_path():
                    lookup_err = dberr.get_path()
                    if lookup_err.is_not_found():
                        pass
                    else:
                        raise e
                else:
                    raise e
        pstat = src.stat()
        src_mtime = datetime.datetime( *time.gmtime( pstat.st_mtime )[:6] )
        if tgt_meta:
            # get size and mtime for both src and tgt
            src_size = pstat.st_size
            logging.debug( '<<<local mtime: {}'.format( src_mtime ) )
            logging.debug( '<<<local size: {}'.format( src_size ) )
            tgt_mtime = tgt_meta.client_modified
            tgt_size = tgt_meta.size
            logging.debug( '>>> tgt mtime: {}'.format( tgt_mtime ) )
            logging.debug( '>>> tgt size: {}'.format( tgt_size ) )
            # compare size and mtime
            if src_mtime == tgt_mtime and src_size == tgt_size:
                # files are already in sync
                tgt_needs_update = False
        if tgt_needs_update:
            self.upload_file( src, tgt, mtime=src_mtime )


    def upload_file( self, src, tgt, mtime ):
        ''' Upload the file with the specified mtime.
            This method does not compare metadata, it just blindly uploads 
            the file.
            To compare metadata first, use the sync_file method.
            INPUT:
                src - pathlib.Path
                tgt - pathlib.Path
                mtime - datetime.datetime *in UTC format*
        '''
        logging.debug( 'Upload file: {} >> {}'.format( src, tgt ) )
        with src.open( mode='rb' ) as f:
            data = f.read()
        res = self.dbx.files_upload( data, 
                                     tgt.as_posix(),
                                     mode = dropbox.files.WriteMode.overwrite,
                                     client_modified = mtime,
                                     mute = False )
        logging.info( 'Upload success: {} {} {}'.format( 
            res.path_display, res.size, res.client_modified ) )


def run():
    dbx = Dropbox_Sync()
    WWW = pathlib.Path( '/var/www/html' )
    TGT = pathlib.Path( '/' )
    for d in ( 'css', 'js', 'font', ):
        dbx.sync_dir( WWW/d, TGT/d )
    dbx.sync_file( WWW/'brewpi_logo.png', TGT/'brewpi_logo.png' )
    dbx.sync_dir( WWW/'data', TGT )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s-%(filename)s[%(lineno)d]-%(funcName)s-%(message)s"
        )
    run()
