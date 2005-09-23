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
""" GenericSetup product exceptions.

$Id: exceptions.py,v 1.1.1.1 2005/08/08 19:38:37 tseaver Exp $
"""

from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo('Products.GenericSetup.exceptions')

security.declarePublic('BadRequest')
from zExceptions import BadRequest
