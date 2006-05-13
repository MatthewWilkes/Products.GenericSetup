##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PythonScript export / import support.

$Id$
"""

from Products.GenericSetup.utils import BodyAdapterBase

from interfaces import IPageTemplate


class PageTemplateBodyAdapter(BodyAdapterBase):

    """Body im- and exporter for PythonScript.
    """

    __used_for__ = IPageTemplate

    def _exportBody(self):
        """Export the object as a file body.
        """
        if self.context.meta_type == 'Page Template':
            return self.context.read()
        return None

    def _importBody(self, body):
        """Import the object from the file body.
        """
        self.context.write(body)

    body = property(_exportBody, _importBody)

    mime_type = 'text/html'

    suffix = '.pt'
