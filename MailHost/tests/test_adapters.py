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
"""MailHost node adapter unit tests.

$Id$
"""

import unittest
import Testing

import Products.Five
import Products.GenericSetup.MailHost
from Products.Five import zcml
from Products.GenericSetup.testing import NodeAdapterTestCase
from zope.app.tests.placelesssetup import PlacelessSetup


_MAILHOST_XML = """\
<object name="foo_mailhost" meta_type="Mail Host" smtp_host="localhost"
   smtp_port="25" smtp_pwd="" smtp_uid=""/>
"""


class MailHostNodeAdapterTests(PlacelessSetup, NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.GenericSetup.MailHost.adapters \
                import MailHostNodeAdapter

        return MailHostNodeAdapter

    def setUp(self):
        from Products.MailHost.MailHost import MailHost

        PlacelessSetup.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.GenericSetup.MailHost)

        self._obj = MailHost('foo_mailhost')
        self._XML = _MAILHOST_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MailHostNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
