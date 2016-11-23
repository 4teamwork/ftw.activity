from ftw.activity.testing import FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getUtility
import transaction


class FunctionalTestCase(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def enable_discussion_for_document(self):
        registry = getUtility(IRegistry)
        registry['plone.app.discussion.interfaces'
                 '.IDiscussionSettings.globally_enabled'] = True

        types = getToolByName(self.portal, 'portal_types')
        types['Document'].allow_discussion = True
