##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Various context implementations for export / import of configurations.

Wrappers representing the state of an import / export operation.

$Id$
"""

import os
import time
from StringIO import StringIO
from tarfile import TarFile
from tarfile import TarInfo

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_self
from Acquisition import Implicit
from DateTime.DateTime import DateTime
from Globals import InitializeClass
from OFS.DTMLDocument import DTMLDocument
from OFS.Folder import Folder
from OFS.Image import File
from OFS.Image import Image
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PythonScripts.PythonScript import PythonScript
from zope.interface import implements

from interfaces import IExportContext
from interfaces import IImportContext
from permissions import ManagePortal

class BaseContext( Implicit ):

    security = ClassSecurityInfo()

    def __init__( self, tool, encoding ):

        self._tool = tool
        self._site = aq_parent( aq_inner( tool ) )
        self._notes = []
        self._encoding = encoding

    security.declareProtected( ManagePortal, 'getSite' )
    def getSite( self ):

        """ See ISetupContext.
        """
        return aq_self(self._site)

    security.declareProtected( ManagePortal, 'getSetupTool' )
    def getSetupTool( self ):

        """ See ISetupContext.
        """
        return self._tool

    security.declareProtected( ManagePortal, 'getEncoding' )
    def getEncoding( self ):

        """ See ISetupContext..
        """
        return self._encoding

    security.declareProtected( ManagePortal, 'notes' )
    def note( self, category, message ):

        """ See ISetupContext.
        """
        self._notes.append( ( category, message ) )

class DirectoryImportContext( BaseContext ):

    implements(IImportContext)

    security = ClassSecurityInfo()

    def __init__( self
                , tool
                , profile_path
                , should_purge=False
                , encoding=None
                ):

        BaseContext.__init__( self, tool, encoding )
        self._profile_path = profile_path
        self._should_purge = bool( should_purge )

    security.declareProtected( ManagePortal, 'readDataFile' )
    def readDataFile( self, filename, subdir=None ):

        """ See IImportContext.
        """
        if subdir is None:
            full_path = os.path.join( self._profile_path, filename )
        else:
            full_path = os.path.join( self._profile_path, subdir, filename )

        if not os.path.exists( full_path ):
            return None

        file = open( full_path, 'rb' )
        result = file.read()
        file.close()

        return result

    security.declareProtected( ManagePortal, 'getLastModified' )
    def getLastModified( self, path ):

        """ See IImportContext.
        """
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ):
            return None

        return DateTime( os.path.getmtime( full_path ) )

    security.declareProtected( ManagePortal, 'isDirectory' )
    def isDirectory( self, path ):

        """ See IImportContext.
        """
        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ):
            return None

        return os.path.isdir( full_path )

    security.declareProtected( ManagePortal, 'listDirectory' )
    def listDirectory( self, path, skip=('CVS', '.svn') ):

        """ See IImportContext.
        """
        if path is None:
            path = ''

        full_path = os.path.join( self._profile_path, path )

        if not os.path.exists( full_path ) or not os.path.isdir( full_path ):
            return None

        names = os.listdir( full_path )

        return [ name for name in names if name not in skip ]

    security.declareProtected( ManagePortal, 'shouldPurge' )
    def shouldPurge( self ):

        """ See IImportContext.
        """
        return self._should_purge

InitializeClass( DirectoryImportContext )


class DirectoryExportContext( BaseContext ):

    implements(IExportContext)

    security = ClassSecurityInfo()

    def __init__( self, tool, profile_path, encoding=None ):

        BaseContext.__init__( self, tool, encoding )
        self._profile_path = profile_path

    security.declareProtected( ManagePortal, 'writeDataFile' )
    def writeDataFile( self, filename, text, content_type, subdir=None ):

        """ See IExportContext.
        """
        if subdir is None:
            prefix = self._profile_path
        else:
            prefix = os.path.join( self._profile_path, subdir )

        full_path = os.path.join( prefix, filename )

        if not os.path.exists( prefix ):
            os.makedirs( prefix )

        mode = content_type.startswith( 'text/' ) and 'w' or 'wb'

        file = open( full_path, mode )
        file.write( text )
        file.close()

InitializeClass( DirectoryExportContext )


class TarballImportContext( BaseContext ):

    implements(IImportContext)

    security = ClassSecurityInfo()

    def __init__( self, tool, archive_bits, encoding=None, should_purge=False ):

        BaseContext.__init__( self, tool, encoding )
        timestamp = time.gmtime()
        self._archive_stream = StringIO(archive_bits)
        self._archive = TarFile.open( 'foo.bar', 'r:gz'
                                    , self._archive_stream )
        self._should_purge = bool( should_purge )

    def readDataFile( self, filename, subdir=None ):

        """ See IImportContext.
        """
        if subdir is not None:
            filename = '/'.join( ( subdir, filename ) )

        try:
            file = self._archive.extractfile( filename )
        except KeyError:
            return None

        return file.read()

    def getLastModified( self, path ):

        """ See IImportContext.
        """
        info = self._getTarInfo( path )
        return info and info.mtime or None

    def isDirectory( self, path ):

        """ See IImportContext.
        """
        info = self._getTarInfo( path )

        if info is not None:
            return info.isdir()

    def listDirectory( self, path, skip=('CVS', '.svn') ):

        """ See IImportContext.
        """
        if path is None:  # root is special case:  no leading '/'
            path = ''
        else:
            if not self.isDirectory(path):
                return None

            if path[-1] != '/':
                path = path + '/'

        pfx_len = len(path)

        beneath = [x[pfx_len:] for x in self._archive.getnames()
                                if x.startswith(path) and x != path]

        return [x for x in beneath if '/' not in x and x not in skip]

    def shouldPurge( self ):

        """ See IImportContext.
        """
        return self._should_purge

    def _getTarInfo( self, path ):
        if path[-1] == '/':
            path = path[:-1]
        try:
            return self._archive.getmember( path )
        except KeyError:
            pass
        try:
            return self._archive.getmember( path + '/' )
        except KeyError:
            return None


class TarballExportContext( BaseContext ):

    implements(IExportContext)

    security = ClassSecurityInfo()

    def __init__( self, tool, encoding=None ):

        BaseContext.__init__( self, tool, encoding )

        timestamp = time.gmtime()
        archive_name = ( 'setup_tool-%4d%02d%02d%02d%02d%02d.tar.gz'
                       % timestamp[:6] )

        self._archive_stream = StringIO()
        self._archive_filename = archive_name
        self._archive = TarFile.open( archive_name, 'w:gz'
                                    , self._archive_stream )

    security.declareProtected( ManagePortal, 'writeDataFile' )
    def writeDataFile( self, filename, text, content_type, subdir=None ):

        """ See IExportContext.
        """
        if subdir is not None:
            filename = '/'.join( ( subdir, filename ) )

        stream = StringIO( text )
        info = TarInfo( filename )
        info.size = len( text )
        info.mtime = time.time()
        self._archive.addfile( info, stream )

    security.declareProtected( ManagePortal, 'getArchive' )
    def getArchive( self ):

        """ Close the archive, and return it as a big string.
        """
        self._archive.close()
        return self._archive_stream.getvalue()

    security.declareProtected( ManagePortal, 'getArchiveFilename' )
    def getArchiveFilename( self ):

        """ Close the archive, and return it as a big string.
        """
        return self._archive_filename

InitializeClass( TarballExportContext )


class SnapshotExportContext( BaseContext ):

    implements(IExportContext)

    security = ClassSecurityInfo()

    def __init__( self, tool, snapshot_id, encoding=None ):

        BaseContext.__init__( self, tool, encoding )
        self._snapshot_id = snapshot_id

    security.declareProtected( ManagePortal, 'writeDataFile' )
    def writeDataFile( self, filename, text, content_type, subdir=None ):

        """ See IExportContext.
        """
        folder = self._ensureSnapshotsFolder( subdir )

        # TODO: switch on content_type
        ob = self._createObjectByType( filename, text, content_type )
        folder._setObject( str( filename ), ob ) # No Unicode IDs!

    security.declareProtected( ManagePortal, 'getSnapshotURL' )
    def getSnapshotURL( self ):

        """ See IExportContext.
        """
        return '%s/%s' % ( self._tool.absolute_url(), self._snapshot_id )

    security.declareProtected( ManagePortal, 'getSnapshotFolder' )
    def getSnapshotFolder( self ):

        """ See IExportContext.
        """
        return self._ensureSnapshotsFolder()

    #
    #   Helper methods
    #
    security.declarePrivate( '_createObjectByType' )
    def _createObjectByType( self, name, body, content_type ):

        if isinstance( body, unicode ):
            encoding = self.getEncoding()
            if encoding is None:
                body = body.encode()
            else:
                body = body.encode( encoding )

        if name.endswith('.py'):

            ob = PythonScript( name )
            ob.write( body )

        elif name.endswith('.dtml'):

            ob = DTMLDocument( '', __name__=name )
            ob.munge( body )

        elif content_type in ('text/html', 'text/xml' ):

            ob = ZopePageTemplate( name, body
                                 , content_type=content_type )

        elif content_type[:6]=='image/':

            ob=Image( name, '', body, content_type=content_type )

        else:
            ob=File( name, '', body, content_type=content_type )

        return ob

    security.declarePrivate( '_ensureSnapshotsFolder' )
    def _ensureSnapshotsFolder( self, subdir=None ):

        """ Ensure that the appropriate snapshot folder exists.
        """
        path = [ 'snapshots', self._snapshot_id ]

        if subdir is not None:
            path.extend( subdir.split( '/' ) )

        current = self._tool

        for element in path:

            if element not in current.objectIds():
                # No Unicode IDs!
                current._setObject( str( element ), Folder( element ) )

            current = current._getOb( element )

        return current

InitializeClass( SnapshotExportContext )


class SnapshotImportContext( BaseContext ):

    implements(IImportContext)

    security = ClassSecurityInfo()

    def __init__( self
                , tool
                , snapshot_id
                , should_purge=False
                , encoding=None
                ):

        BaseContext.__init__( self, tool, encoding )
        self._snapshot_id = snapshot_id
        self._encoding = encoding
        self._should_purge = bool( should_purge )

    security.declareProtected( ManagePortal, 'readDataFile' )
    def readDataFile( self, filename, subdir=None ):

        """ See IImportContext.
        """
        try:
            snapshot = self._getSnapshotFolder( subdir )
            object = snapshot._getOb( filename )
        except ( AttributeError, KeyError ):
            return None

        try:
            return object.read()
        except AttributeError:
            return object.manage_FTPget()

    security.declareProtected( ManagePortal, 'getLastModified' )
    def getLastModified( self, path ):

        """ See IImportContext.
        """
        try:
            snapshot = self._getSnapshotFolder()
            object = snapshot.restrictedTraverse( path )
        except ( AttributeError, KeyError ):
            return None
        else:
            return object.bobobase_modification_time()

    security.declareProtected( ManagePortal, 'isDirectory' )
    def isDirectory( self, path ):

        """ See IImportContext.
        """
        try:
            snapshot = self._getSnapshotFolder()
            object = snapshot.restrictedTraverse( path )
        except ( AttributeError, KeyError ):
            return None
        else:
            folderish = getattr( object, 'isPrincipiaFolderish', False )
            return bool( folderish )

    security.declareProtected( ManagePortal, 'listDirectory' )
    def listDirectory( self, path, skip=() ):

        """ See IImportContext.
        """
        try:
            snapshot = self._getSnapshotFolder()
            subdir = snapshot.restrictedTraverse( path )
        except ( AttributeError, KeyError ):
            return None
        else:
            if not getattr( subdir, 'isPrincipiaFolderish', False ):
                return None

            object_ids = subdir.objectIds()
            return [ x for x in object_ids if x not in skip ]

    security.declareProtected( ManagePortal, 'shouldPurge' )
    def shouldPurge( self ):

        """ See IImportContext.
        """
        return self._should_purge

    #
    #   Helper methods
    #
    security.declarePrivate( '_getSnapshotFolder' )
    def _getSnapshotFolder( self, subdir=None ):

        """ Return the appropriate snapshot (sub)folder.
        """
        path = [ 'snapshots', self._snapshot_id ]

        if subdir is not None:
            path.extend( subdir.split( '/' ) )

        return self._tool.restrictedTraverse( path )

InitializeClass( SnapshotImportContext )
