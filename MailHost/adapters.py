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
"""MailHost node adapters.

$Id$
"""

from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import NodeAdapterBase

from Products.MailHost.interfaces import IMailHost


class MailHostNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for MailHost.
    """

    __used_for__ = IMailHost

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.setAttribute('smtp_host', str(self.context.smtp_host))
        node.setAttribute('smtp_port', str(self.context.smtp_port))
        node.setAttribute('smtp_uid', self.context.smtp_uid)
        node.setAttribute('smtp_pwd', self.context.smtp_pwd)
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        self.context.smtp_host = str(node.getAttribute('smtp_host'))
        self.context.smtp_port = int(node.getAttribute('smtp_port'))
        self.context.smtp_uid = node.getAttribute('smtp_uid')
        self.context.smtp_pwd = node.getAttribute('smtp_pwd')
