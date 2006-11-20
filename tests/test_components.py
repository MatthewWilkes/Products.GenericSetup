##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Component registry export / import support unit tests.

$Id$
"""

import unittest
from Testing.ZopeTestCase import ZopeTestCase

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

from zope.app.component.hooks import setSite, clearSite, setHooks
from zope.component import getSiteManager
from zope.component import queryUtility
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents
from zope.interface import implements
from zope.interface import Interface

_marker = []

def createComponentRegistry(context):
    enableSite(context, iface=IObjectManagerSite)

    components = PersistentComponents()
    components.__bases__ = (base,)
    context.setSiteManager(components)

class IDummyInterface(Interface):
    """A dummy interface."""

    def verify():
        """Returns True."""

class IDummyInterface2(Interface):
    """A second dummy interface."""

    def verify():
        """Returns True."""

class DummyUtility(object):
    """A dummy utility."""

    implements(IDummyInterface)

    def verify(self):
        return True

class DummyUtility2(object):
    """A second dummy utility."""

    implements(IDummyInterface2)

    def verify(self):
        return True

dummy2 = DummyUtility2()

class DummyTool(SimpleItem):
    """A dummy tool."""
    implements(IDummyInterface)

    id = 'dummy_tool'
    meta_type = 'dummy tool'
    security = ClassSecurityInfo()

    security.declarePublic('verify')
    def verify(self):
        return True

InitializeClass(DummyTool)

_COMPONENTS_BODY = """\
<?xml version="1.0"?>
<componentregistry>
 <adapters/>
 <utilities>
  <utility factory="Products.GenericSetup.tests.test_components.DummyUtility"
     interface="Products.GenericSetup.tests.test_components.IDummyInterface"/>
  <utility name="dummy tool name"
     interface="Products.GenericSetup.tests.test_components.IDummyInterface"
     object="/dummy_tool"/>
  <utility name="dummy tool name2"
     interface="Products.GenericSetup.tests.test_components.IDummyInterface"
     object="/test_folder_1_/dummy_tool"/>
  <utility name="foo"
     factory="Products.GenericSetup.tests.test_components.DummyUtility"
     interface="Products.GenericSetup.tests.test_components.IDummyInterface"/>
  <utility component="Products.GenericSetup.tests.test_components.dummy2"
     interface="Products.GenericSetup.tests.test_components.IDummyInterface2"/>
 </utilities>
</componentregistry>
"""


class ComponentRegistryXMLAdapterTests(ZopeTestCase, BodyAdapterTestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.components import \
            ComponentRegistryXMLAdapter
        return ComponentRegistryXMLAdapter

    def _verifyImport(self, obj):
        util = queryUtility(IDummyInterface, name=u'foo')
        self.failUnless(IDummyInterface.providedBy(util))
        self.failUnless(util.verify())

        util = queryUtility(IDummyInterface)
        self.failUnless(IDummyInterface.providedBy(util))
        self.failUnless(util.verify())

        util = queryUtility(IDummyInterface, name='dummy tool name')
        self.failUnless(IDummyInterface.providedBy(util))
        self.failUnless(util.verify())
        self.assertEqual(util.meta_type, 'dummy tool')

        # make sure we can get the tool by normal means
        tool = getattr(self.app, 'dummy_tool')
        self.assertEqual(tool.meta_type, 'dummy tool')
        self.assertEquals(repr(util), repr(tool))

        util = queryUtility(IDummyInterface2)
        self.failUnless(IDummyInterface2.providedBy(util))
        self.failUnless(util.verify())

        util = queryUtility(IDummyInterface, name='dummy tool name2')
        self.failUnless(IDummyInterface.providedBy(util))
        self.failUnless(util.verify())
        self.assertEqual(util.meta_type, 'dummy tool')

        # make sure we can get the tool by normal means
        tool = getattr(self.app.test_folder_1_, 'dummy_tool2')
        self.assertEqual(tool.meta_type, 'dummy tool')
        self.assertEquals(repr(util), repr(tool))

    def afterSetUp(self):
        BodyAdapterTestCase.setUp(self)

        # Create and enable a local component registry
        createComponentRegistry(self.app)
        setHooks()
        setSite(self.app)
        sm = getSiteManager()

        sm.registerUtility(DummyUtility(), IDummyInterface)
        sm.registerUtility(DummyUtility(), IDummyInterface, name=u'foo')
        sm.registerUtility(dummy2, IDummyInterface2)

        tool = DummyTool()
        self.app._setObject(tool.id, tool)
        obj = self.app[tool.id]
        sm.registerUtility(obj, IDummyInterface, name=u'dummy tool name')

        folder = self.app.test_folder_1_
        tool2 = DummyTool()
        folder._setObject('dummy_tool2', tool2)
        obj = folder['dummy_tool2']
        sm.registerUtility(obj, IDummyInterface, name=u'dummy tool name2')

        self._obj = sm
        self._BODY = _COMPONENTS_BODY

    def beforeTearDown(self):
        clearSite()


def test_suite():
    # reimport to make sure tests are run from Products
    from Products.GenericSetup.tests.test_components \
            import ComponentRegistryXMLAdapterTests

    return unittest.TestSuite((
        unittest.makeSuite(ComponentRegistryXMLAdapterTests),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())
