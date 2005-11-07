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
"""Node adapter testing utils.

$Id$
"""

import unittest
from xml.dom.minidom import parseString

from zope.interface.verify import verifyClass

from interfaces import INodeExporter
from interfaces import INodeImporter
from utils import PrettyDocument

try:
    from zope.app.testing.placelesssetup import PlacelessSetup
except ImportError:  # BBB, Zope3 < 3.1
    from zope.app.tests.placelesssetup import PlacelessSetup


class NodeAdapterTestCase(unittest.TestCase):

    def _populate(self, obj):
        pass

    def test_z3interfaces(self):
        verifyClass(INodeExporter, self._getTargetClass())
        verifyClass(INodeImporter, self._getTargetClass())

    def test_exportNode(self):
        self._populate(self._obj)
        node = INodeExporter(self._obj).exportNode(PrettyDocument())
        self.assertEqual(node.toprettyxml(' '), self._XML)

    def test_importNode(self):
        node = parseString(self._XML).documentElement
        self.assertEqual(INodeImporter(self._obj).importNode(node), None)
        node = INodeExporter(self._obj).exportNode(PrettyDocument())
        self.assertEqual(node.toprettyxml(' '), self._XML)
