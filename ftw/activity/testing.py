from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig
import ftw.activity.tests.builders


class ActivityLayer(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '  <include package="ftw.activity.tests" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.activity:default')
        applyProfile(portal, 'ftw.activity.tests:dexterity')


ACTIVITY_FIXTURE = ActivityLayer()
FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(ACTIVITY_FIXTURE,
               set_builder_session_factory(functional_session_factory)),
        name="functional")
