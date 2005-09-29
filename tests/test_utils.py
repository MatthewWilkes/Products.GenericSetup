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
""" GenericSetup.utils unit tests

$Id$
"""

import unittest
import Testing

from xml.dom.minidom import parseString

from Products.GenericSetup.interfaces import PURGE, UPDATE
from Products.GenericSetup.utils import PrettyDocument


_EMPTY_PROPERTY_EXPORT = """\
<?xml version="1.0"?>
<dummy>
 <property name="foo_boolean" type="boolean">False</property>
 <property name="foo_date" type="date"></property>
 <property name="foo_float" type="float"></property>
 <property name="foo_int" type="int"></property>
 <property name="foo_lines" type="lines"></property>
 <property name="foo_long" type="long"></property>
 <property name="foo_string" type="string"></property>
 <property name="foo_text" type="text"></property>
 <property name="foo_tokens" type="tokens"/>
 <property name="foo_selection" select_variable="foobarbaz" \
type="selection"></property>
 <property name="foo_mselection" select_variable="foobarbaz" \
type="multiple selection"/>
 <property name="foo_boolean0" type="boolean">False</property>
</dummy>
"""

_NORMAL_PROPERTY_EXPORT = """\
<?xml version="1.0"?>
<dummy>
 <property name="foo_boolean" type="boolean">True</property>
 <property name="foo_date" type="date">2000/01/01</property>
 <property name="foo_float" type="float">1.1</property>
 <property name="foo_int" type="int">1</property>
 <property name="foo_lines" type="lines">
  <element value="Foo"/>
  <element value="Lines"/>
 </property>
 <property name="foo_long" type="long">1</property>
 <property name="foo_string" type="string">Foo String</property>
 <property name="foo_text" type="text">Foo
Text</property>
 <property name="foo_tokens" type="tokens">
  <element value="Foo"/>
  <element value="Tokens"/>
 </property>
 <property name="foo_selection" select_variable="foobarbaz" \
type="selection">Foo</property>
 <property name="foo_mselection" select_variable="foobarbaz" \
type="multiple selection">
  <element value="Foo"/>
  <element value="Baz"/>
 </property>
 <property name="foo_boolean0" type="boolean">False</property>
</dummy>
"""

_FIXED_PROPERTY_EXPORT = """\
<?xml version="1.0"?>
<dummy>
 <property name="foo_boolean">True</property>
 <property name="foo_date">2000/01/01</property>
 <property name="foo_float">1.1</property>
 <property name="foo_int">1</property>
 <property name="foo_lines">
  <element value="Foo"/>
  <element value="Lines"/>
 </property>
 <property name="foo_long">1</property>
 <property name="foo_string">Foo String</property>
 <property name="foo_text">Foo
Text</property>
 <property name="foo_tokens">
  <element value="Foo"/>
  <element value="Tokens"/></property>
 <property name="foo_selection" type="selection" \
select_variable="foobarbaz">Foo</property>
 <property name="foo_mselection">
  <element value="Foo"/>
  <element value="Baz"/>
 </property>
 <property name="foo_boolean0">False</property>
</dummy>
"""

_SPECIAL_IMPORT = """\
<?xml version="1.0"?>
<dummy>
 <!-- ignore comment, import 0 as False -->
 <property name="foo_boolean0" type="boolean">0</property>
</dummy>
"""


def _testFunc( *args, **kw ):

    """ This is a test.

    This is only a test.
    """

_TEST_FUNC_NAME = 'Products.GenericSetup.tests.test_utils._testFunc'

class Whatever:
    pass

_WHATEVER_NAME = 'Products.GenericSetup.tests.test_utils.Whatever'

whatever_inst = Whatever()
whatever_inst.__name__ = 'whatever_inst'

_WHATEVER_INST_NAME = 'Products.GenericSetup.tests.test_utils.whatever_inst'

class UtilsTests( unittest.TestCase ):

    def test__getDottedName_simple( self ):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( _testFunc ), _TEST_FUNC_NAME )

    def test__getDottedName_string( self ):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( _TEST_FUNC_NAME ), _TEST_FUNC_NAME )

    def test__getDottedName_unicode( self ):

        from Products.GenericSetup.utils import _getDottedName

        dotted = u'%s' % _TEST_FUNC_NAME
        self.assertEqual( _getDottedName( dotted ), _TEST_FUNC_NAME )
        self.assertEqual( type( _getDottedName( dotted ) ), str )

    def test__getDottedName_class( self ):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( Whatever ), _WHATEVER_NAME )

    def test__getDottedName_inst( self ):

        from Products.GenericSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( whatever_inst )
                        , _WHATEVER_INST_NAME )

    def test__getDottedName_noname( self ):

        from Products.GenericSetup.utils import _getDottedName

        class Doh:
            pass

        doh = Doh()
        self.assertRaises( ValueError, _getDottedName, doh )


class PropertyManagerHelpersTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.GenericSetup.utils import PropertyManagerHelpers

        return PropertyManagerHelpers

    def _makeOne(self, *args, **kw):
        from Products.GenericSetup.utils import NodeAdapterBase

        class Foo(self._getTargetClass(), NodeAdapterBase):

            pass

        return Foo(*args, **kw)

    def setUp(self):
        from OFS.PropertyManager import PropertyManager

        obj = PropertyManager('obj')
        obj.foobarbaz = ('Foo', 'Bar', 'Baz')
        obj._properties = ()
        obj._setProperty('foo_boolean', '', 'boolean')
        obj._setProperty('foo_date', '', 'date')
        obj._setProperty('foo_float', '', 'float')
        obj._setProperty('foo_int', '', 'int')
        obj._setProperty('foo_lines', '', 'lines')
        obj._setProperty('foo_long', '', 'long')
        obj._setProperty('foo_string', '', 'string')
        obj._setProperty('foo_text', '', 'text')
        obj._setProperty('foo_tokens', (), 'tokens')
        obj._setProperty('foo_selection', 'foobarbaz', 'selection')
        obj._setProperty('foo_mselection', 'foobarbaz', 'multiple selection')
        obj._setProperty('foo_boolean0', '', 'boolean')
        self.helpers = self._makeOne(obj)

    def _populate(self, obj):
        obj._updateProperty('foo_boolean', 'True')
        obj._updateProperty('foo_date', '2000/01/01')
        obj._updateProperty('foo_float', '1.1')
        obj._updateProperty('foo_int', '1')
        obj._updateProperty('foo_lines', 'Foo\nLines')
        obj._updateProperty('foo_long', '1')
        obj._updateProperty('foo_string', 'Foo String')
        obj._updateProperty('foo_text', 'Foo\nText')
        obj._updateProperty( 'foo_tokens', ('Foo', 'Tokens') )
        obj._updateProperty('foo_selection', 'Foo')
        obj._updateProperty( 'foo_mselection', ('Foo', 'Baz') )
        obj.foo_boolean0 = 0

    def test__extractProperties_empty(self):
        doc = self.helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(self.helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _EMPTY_PROPERTY_EXPORT)

    def test__extractProperties_normal(self):
        self._populate(self.helpers.context)
        doc = self.helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(self.helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_normal(self):
        node = parseString(_NORMAL_PROPERTY_EXPORT).documentElement
        self.helpers._initProperties(node, PURGE)

        doc = self.helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(self.helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_fixed(self):
        node = parseString(_FIXED_PROPERTY_EXPORT).documentElement
        self.helpers._initProperties(node, PURGE)

        doc = self.helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(self.helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _NORMAL_PROPERTY_EXPORT)

    def test__initProperties_special(self):
        node = parseString(_SPECIAL_IMPORT).documentElement
        self.helpers._initProperties(node, UPDATE)

        doc = self.helpers._doc = PrettyDocument()
        node = doc.createElement('dummy')
        node.appendChild(self.helpers._extractProperties())
        doc.appendChild(node)

        self.assertEqual(doc.toprettyxml(' '), _EMPTY_PROPERTY_EXPORT)


def test_suite():
    # reimport to make sure tests are run from Products
    from Products.GenericSetup.tests.test_utils import UtilsTests

    return unittest.TestSuite((
        unittest.makeSuite(UtilsTests),
        unittest.makeSuite(PropertyManagerHelpersTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
