# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from posixpath import join
from io import BytesIO
from uuid import uuid1
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
import logging

__all__ = ['pathbuilderError', 'pathbuilder']

logging.getLogger('hcpsdk.pathbuilder').addHandler(logging.NullHandler())


class pathbuilderError(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # or define self.args.  Otherwise, str() will fail.
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason


class pathbuilder(object):
    '''
    Conversion of a filename into a unique object name and a proper path for HCPs
    needs. Re-conversion of a unique object name to the path where the object can
    be found in HCP.
    '''

    def __init__(self, initialpath='/rest/hcpsdk', annotation=False):
        '''
        :param initialpath: the leading part of the path
        :param annotation:  if True, create an XML structure to be used as custom
                            metadata annotation containing a tag with the
                            original filename of the object.
        '''
        self.logger = logging.getLogger(__name__)
        self.leadingpath = initialpath
        self.annotation = annotation


    def getunique(self, filename):
        '''
        Build a unique path / object name scheme.

        The path is build from **initialpath** given during class instantiation
        plus byte 4 and 3 of the UUID in hexadecimal.

        If **annotation** is True during class instantiation, there will be
        a third element in the returned tuple, containing an XML structure that
        can be used as custom metadata annotation for the object.

        :param filename:    the filename to be transformed
        :return:            a tuple consisting of path, unique object name and
                            -eventually- an annotation string.
        :raises:            hcpsdk.pathbuilder.pathbuilderError

        **Example:**

        ::

            >>> from hcpsdk.pathbuilder import pathbuilder
            >>> p = pathbuilder(initialpath='/rest/mypath', annotation=True)
            >>> o = p.getunique('testfile.txt')
            >>> o
            ('/rest/mypath/ee/46', '418646ee-9663-11e4-85a6-00059a3c7800',
             '<?xml version=\'1.0\' encoding=\'cp1252\'?>
                <hcpsdk_fileobject
                    filename="testfile.txt"
                    path="/rest/mypath/ee/46"
                    uuid="418646ee-9663-11e4-85a6-00059a3c7800"
              />')
            >>>
        '''
        try:
            uuid = str(uuid1())
            path = join(self.leadingpath, uuid[6:8], uuid[4:6])
            if self.annotation:
                xml = ElementTree()
                e = Element('hcpsdk_fileobject', {'filename': filename,
                                                       'path': path,
                                                       'uuid': uuid})
                xml._setroot(e)
                with BytesIO() as xmlstring:
                    xml.write(xmlstring, encoding="utf-8", method="xml", xml_declaration=True)
                    annotation = xmlstring.getvalue().decode()
        except Exception as e:
            raise pathbuilderError(str(e))

        if self.annotation:
            return(path, uuid, annotation)
        else:
            return(path, uuid)


    def getpath(self, objectname):
        '''
        From a unique object name, retrieve the path in which the object was stored.

        :param objectname:  an unique object name
        :return:            the full path to the object (including its name)
        :raises:            hcpsdk.pathbuilder.pathbuilderError

        **Example:**

        ::

            >>> p.getpath("418646ee-9663-11e4-85a6-00059a3c7800")
            '/rest/mypath/ee/46/418646ee-9663-11e4-85a6-00059a3c7800'
            >>>
        '''
        try:
            path = join(self.leadingpath, objectname[6:8], objectname[4:6], objectname)
        except Exception as e:
            raise pathbuilderError(str(e))

        return path
