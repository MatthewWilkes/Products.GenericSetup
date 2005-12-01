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
import Testing

from xml.dom.minidom import parseString

import Products.Five
from Products.Five import zcml
from zope.app import zapi
from zope.interface.verify import verifyClass

from interfaces import IBody
from interfaces import INodeExporter
from interfaces import INodeImporter
from tests.common import DummyExportContext
from tests.common import DummyImportContext
from utils import PrettyDocument

try:
    from zope.app.testing.placelesssetup import PlacelessSetup
except ImportError:  # BBB, Zope3 < 3.1
    from zope.app.tests.placelesssetup import PlacelessSetup


class BodyAdapterTestCase(PlacelessSetup, unittest.TestCase):

    def _populate(self, obj):
        pass

    def _verifyImport(self, obj):
        pass

    def setUp(self):
        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_z3interfaces(self):
        verifyClass(IBody, self._getTargetClass())

    def test_body_get(self):
        self._populate(self._obj)
        context = DummyExportContext(None)
        exporter = zapi.getMultiAdapter((self._obj, context), IBody)
        self.assertEqual(exporter.body, self._BODY)

    def test_body_set(self):
        context = DummyImportContext(None)
        importer = zapi.getMultiAdapter((self._obj, context), IBody)
        importer.body = self._BODY
        self._verifyImport(self._obj)
        context = DummyExportContext(None)
        exporter = zapi.getMultiAdapter((self._obj, context), IBody)
        self.assertEqual(exporter.body, self._BODY)


class NodeAdapterTestCase(PlacelessSetup, unittest.TestCase):

    def _populate(self, obj):
        pass

    def _verifyImport(self, obj):
        pass

    def setUp(self):
        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

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
        self._verifyImport(self._obj)
        node = INodeExporter(self._obj).exportNode(PrettyDocument())
        self.assertEqual(node.toprettyxml(' '), self._XML)
