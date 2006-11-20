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
"""Local component registry export / import handler.

$Id$
"""

from zope.app.component.hooks import getSite
from zope.component import adapts
from zope.component import getSiteManager
from zope.component.interfaces import IComponentRegistry
from zope.interface import implements

from interfaces import IBody
from interfaces import ISetupEnviron
from utils import XMLAdapterBase
from utils import exportObjects
from utils import importObjects
from utils import _getDottedName
from utils import _resolveDottedName


class ComponentRegistryXMLAdapter(XMLAdapterBase):

    """XML im- and exporter for a local component registry.
    """

    adapts(IComponentRegistry, ISetupEnviron)

    _LOGGER_ID = 'componentregistry'

    name = 'componentregistry'

    def _exportNode(self):
        node=self._doc.createElement('componentregistry')
        fragment = self._doc.createDocumentFragment()

        child=self._doc.createElement('adapters')
        child.appendChild(self._extractAdapters())
        self._logger.info('Adapters exported.')
        fragment.appendChild(child)

        child=self._doc.createElement('utilities')
        child.appendChild(self._extractUtilities())
        self._logger.info('Utilities exported.')
        fragment.appendChild(child)

        node.appendChild(fragment)

        return node

    def _importNode(self, node):
        if self.environ.shouldPurge():
            self._purgeAdapters()
            self._purgeUtilities()

        for child in node.childNodes:
            if child.nodeName == 'adapters':
                self._initAdapters(child)
                self._logger.info('Adapters registered.')
            if child.nodeName == 'utilities':
                self._initUtilities(child)
                self._logger.info('Utilities registered.')

    def _purgeAdapters(self):
        registrations = self.context.registeredAdapters()
        
        for registration in registrations:
            factory = registration.factory
            required = registration.required
            provided = registration.provided
            name = registration.name

            self.context.unregisterAdapter(factory=factory,
                                           required=required,
                                           provided=provided,
                                           name=name)

    def _purgeUtilities(self):
        registrations = self.context.registeredAdapters()
        
        for registration in registrations:
            provided = registration.provided
            name = registration.name
            self.context.unregisterUtility(provided=provided, name=name)

    def _initAdapters(self, node):
        for child in node.childNodes:
            if child.nodeName != 'adapter':
                continue

            factory = _resolveDottedName(child.getAttribute('factory'))
            provided = _resolveDottedName(child.getAttribute('provides'))
            name = unicode(str(child.getAttribute('name')))

            for_ = child.getAttribute('for_')
            required = []
            for interface in for_.split(u' '):
                if interface:
                    required.append(_resolveDottedName(interface))

            self.context.registerAdapter(factory,
                                         required=required,
                                         provided=provided,
                                         name=name)

    def _initUtilities(self, node):
        for child in node.childNodes:
            if child.nodeName != 'utility':
                continue

            provided = _resolveDottedName(child.getAttribute('interface'))
            name = unicode(str(child.getAttribute('name')))

            component = child.getAttribute('component')
            component = component and _resolveDottedName(component) or None

            factory = child.getAttribute('factory')
            factory = factory and _resolveDottedName(factory) or None

            obj_path = child.getAttribute('object')
            if obj_path:
                site = getSite()
                # we support registering aq_wrapped objects only for now
                if hasattr(site, 'aq_base'):
                    # filter out empty path segments
                    path = [f for f in obj_path.split('/') if f]
                    # XXX add support for nested folder
                    if len(path) > 1:
                        return
                    obj = getattr(site, path[0], None)
                    if obj is not None:
                        self.context.registerUtility(obj, provided, name)
                else:
                    # Log an error, not aq_wrapped
                    self._logger.warning("The object %s was not acquisition "
                                         "wrapped. Registering these is not "
                                         "supported right now." % obj)
            elif component:
                self.context.registerUtility(component, provided, name)
            else:
                self.context.registerUtility(factory(), provided, name)

    def _extractAdapters(self):
        fragment = self._doc.createDocumentFragment()

        # We get back a generator but in order to have a consistent order
        # which is needed for the tests we convert to a sorted list
        registrations = [reg for reg in self.context.registeredAdapters()]
        registrations.sort()
        
        for registration in registrations:
            child=self._doc.createElement('adapter')

            factory = _getDottedName(registration.factory)
            provided = _getDottedName(registration.provided)
            name = _getDottedName(registration.name)

            for_ = u''
            for interface in registration.required:
                for_ = for_ + _getDottedName(interface) + u'\n           '

            child.setAttribute('factory', factory)
            child.setAttribute('provides', provided)
            child.setAttribute('for_', for_.strip())
            if name:
                child.setAttribute('name', name)

            fragment.appendChild(child)

        return fragment

    def _extractUtilities(self):
        fragment = self._doc.createDocumentFragment()

        # We get back a generator but in order to have a consistent order
        # which is needed for the tests we convert to a sorted list
        registrations = [reg for reg in self.context.registeredUtilities()]
        registrations.sort()

        for registration in registrations:
            child=self._doc.createElement('utility')

            provided = _getDottedName(registration.provided)
            child.setAttribute('interface', provided)

            name = _getDottedName(registration.name)
            if name:
                child.setAttribute('name', name)

            comp = registration.component
            # check if the component is acquisition wrapped. If it is export
            # an object reference instead of a component / factory reference
            if hasattr(comp, 'aq_base'):
                # if the site is acquistion wrapped as well, get the relative
                # path to the site
                path = '/'.join(comp.getPhysicalPath())
                site = getSite()
                if hasattr(site, 'aq_base'):
                    site_path = '/'.join(site.getPhysicalPath())
                    rel_path = path[len(site_path):]
                child.setAttribute('object', rel_path)
            else:
                factory = _getDottedName(type(comp))
                reference = self.resolveName(comp)
                if reference:
                    module = _getDottedName(comp.__module__)
                    component = "%s.%s" % (module, reference)
                    child.setAttribute('component', component)
                else:
                    child.setAttribute('factory', factory)

            fragment.appendChild(child)

        return fragment

    def resolveName(self, component):
        # extremly ugly hack to get to the reference name, this only
        # works if the utility reference is defined in the namespace of the
        # same module as the class itself
        module = _resolveDottedName(component.__module__)
        namespace = module.__dict__
        name = ''
        for ref in namespace:
            if namespace[ref] is component:
                name = ref
        del module
        del namespace
        return name


def dummyGetId():
    return ''

def importComponentRegistry(context):
    """Import local components.
    """
    sm = getSiteManager(context.getSite())
    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('componentregistry')
        logger.info("Can not register components, as no registry was found.")
        return
    # XXX GenericSetup.utils.importObjects expects the object to have a getId
    # function. We provide a dummy one for now, but this should be fixed in GS
    # itself
    sm.getId = dummyGetId
    importObjects(sm, '', context)
    del(sm.getId)

def exportComponentRegistry(context):
    """Export local components.
    """
    sm = getSiteManager(context.getSite())
    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('componentregistry')
        logger.info("Nothing to export.")
        return
    # XXX GenericSetup.utils.exportObjects expects the object to have a getId
    # function. We provide a dummy one for now, but this should be fixed in GS
    # itself
    sm.getId = dummyGetId
    exportObjects(sm, '', context)
    del(sm.getId)
