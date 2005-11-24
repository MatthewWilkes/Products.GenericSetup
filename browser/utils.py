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
"""GenericSetup browser view utils.

$Id$
"""

class AddWithPresettingsViewBase:

    """Base class for add views with selectable presettings.
    """

    def title(self):
        return u'Add %s' % self.klass.meta_type

    def __call__(self, add_input_name='', settings_id='', submit_add=''):
        if submit_add:
            obj = self.klass('temp')
            if settings_id:
                profile_id, obj_id = settings_id.split('/')
                if not add_input_name:
                    self.request.set('add_input_name', obj_id)
                self._initSettings(obj, profile_id, obj_id)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()
