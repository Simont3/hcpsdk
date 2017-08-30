# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2014-2017 Thorsten Simons (sw@snomis.de)
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

__all__ = ['PathBuilderError', 'PathBuilder']

logging.getLogger('hcpsdk.pathbuilder').addHandler(logging.NullHandler())


class PathBuilderError(Exception):
    """
    Used to signal an error during unique object name generation or object
    name to path mapping.
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


class PathBuilder(object):
    """
    Conversion of a filename into a unique object name and a proper path for HCPs
    needs. Re-conversion of a unique object name to the path where the object can
    be found in HCP.
    """

    def __init__(self, initialpath='/rest/hcpsdk', annotation=False):
        """
        :param initialpath: the leading part of the path
        :param annotation:  if True, create an XML structure to be used as custom
                            metadata annotation containing a tag with the
                            original filename of the object.
        """
        self.logger = logging.getLogger(__name__ + '.PathBuilder')
        self.leadingpath = initialpath
        self.annotation = annotation

    def getunique(self, filename):
        """
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

            >>> from hcpsdk.pathbuilder import PathBuilder
            >>> p = PathBuilder(initialpath='/rest/mypath', annotation=True)
            >>> o = p.getunique('testfile.txt')
            >>> o
            ('/rest/mypath/b4/ec', '8ac8ecb4-9f1e-11e4-a524-98fe94437d8c',
             '<?xml version=\'1.0\' encoding=\'utf-8\'?>
                <hcpsdk_fileobject
                    filename="testfile.txt"
                    path="/rest/mypath/b4/ec"
                    uuid="8ac8ecb4-9f1e-11e4-a524-98fe94437d8c"
             />')
            >>>
        """
        try:
            uuid = str(uuid1())
            path = join(self.leadingpath, uuid[6:8], uuid[4:6])
            if self.annotation:
                xml = ElementTree()
                e = Element('hcpsdk_fileobject', {'filename': filename,
                                                  'path': path,
                                                  'uuid': uuid})
                # noinspection PyProtectedMember
                xml._setroot(e)
                with BytesIO() as xmlstring:
                    xml.write(xmlstring, encoding="utf-8", method="xml", xml_declaration=True)
                    annotation = xmlstring.getvalue().decode()
        except Exception as e:
            raise PathBuilderError(str(e))

        if self.annotation:
            # noinspection PyUnboundLocalVariable
            return path, uuid, annotation
        else:
            return path, uuid

    def getpath(self, objectname):
        """
        From a unique object name, retrieve the path in which the object was stored.

        :param objectname:  an unique object name
        :return:            the full path to the object (including its name)
        :raises:            hcpsdk.pathbuilder.pathbuilderError

        **Example:**

        ::

            >>> p.getpath('8ac8ecb4-9f1e-11e4-a524-98fe94437d8c')
            '/rest/mypath/b4/ec/8ac8ecb4-9f1e-11e4-a524-98fe94437d8c'
            >>>
        """
        try:
            path = join(self.leadingpath, objectname[6:8], objectname[4:6], objectname)
        except Exception as e:
            raise PathBuilderError(str(e))

        return path
