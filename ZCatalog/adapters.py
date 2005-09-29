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
"""ZCatalog node adapters.

$Id$
"""

from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.ZCatalog.interfaces import IZCatalog


class _extra:

    pass


class ZCatalogNodeAdapter(NodeAdapterBase, ObjectManagerHelpers,
                          PropertyManagerHelpers):

    """Node im- and exporter for ZCatalog.
    """

    __used_for__ = IZCatalog

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        node.appendChild(self._extractIndexes())
        node.appendChild(self._extractColumns())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeProperties()
            self._purgeObjects()
            self._purgeIndexes()
            self._purgeColumns()

        self._initProperties(node, mode)
        self._initObjects(node, mode)
        self._initIndexes(node, mode)
        self._initColumns(node, mode)

    def _extractIndexes(self):
        fragment = self._doc.createDocumentFragment()
        indexes = self.context.getIndexObjects()[:]
        indexes.sort(lambda x,y: cmp(x.getId(), y.getId()))
        for idx in indexes:
            fragment.appendChild(INodeExporter(idx).exportNode(self._doc))
        return fragment

    def _purgeIndexes(self):
        for idx_id in self.context.indexes():
            self.context.delIndex(idx_id)

    def _initIndexes(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'index':
                continue
            if child.hasAttribute('deprecated'):
                continue
            zcatalog = self.context

            idx_id = str(child.getAttribute('name'))
            if idx_id not in zcatalog.indexes():
                extra = _extra()
                for sub in child.childNodes:
                    if sub.nodeName == 'extra':
                        name = str(sub.getAttribute('name'))
                        value = str(sub.getAttribute('value'))
                        setattr(extra, name, value)
                extra = extra.__dict__ and extra or None

                meta_type = str(child.getAttribute('meta_type'))
                zcatalog.addIndex(idx_id, meta_type, extra)

            idx = zcatalog._catalog.getIndex(idx_id)
            INodeImporter(idx).importNode(child, mode)

    def _extractColumns(self):
        fragment = self._doc.createDocumentFragment()
        schema = self.context.schema()[:]
        schema.sort()
        for col in schema:
            child = self._doc.createElement('column')
            child.setAttribute('value', col)
            fragment.appendChild(child)
        return fragment

    def _purgeColumns(self):
        for col in self.context.schema()[:]:
            self.context.delColumn(col)

    def _initColumns(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'column':
                continue
            col = str(child.getAttribute('value'))
            if col not in self.context.schema()[:]:
                self.context.addColumn(col)
