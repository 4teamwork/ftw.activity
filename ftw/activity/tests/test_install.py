from datetime import datetime
from DateTime import DateTime
from ftw.activity.catalog import get_activity_soup
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.helpers import get_soup_activities
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestInstalling(TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal_setup = getToolByName(self.portal, 'portal_setup')

    def test_default_profile_installed(self):
        version = self.portal_setup.getLastVersionForProfile(
            'ftw.activity:default')
        self.assertNotEqual(version, None)
        self.assertNotEqual(version, 'unknown')

    def test_existing_objects_are_indexed_when_installing(self):
        with freeze(datetime(2010, 1, 1)):
            folder = create(Builder('folder'))
        with freeze(datetime(2010, 1, 2)):
            create(Builder('document'))
        with freeze(datetime(2010, 1, 3)):
            create(Builder('document').within(folder))
        with freeze(datetime(2010, 1, 4)):
            folder.notifyModified()

        get_activity_soup().clear()
        applyProfile(self.portal, 'ftw.activity:default')

        self.maxDiff = None
        self.assertEquals(
            [{'path': '/plone/folder',
              'action': 'added',
              'date': DateTime('2010/01/01')},
             {'path': '/plone/document',
              'action': 'added',
              'date': DateTime('2010/01/02')},
             {'path': '/plone/folder/document',
              'action': 'added',
              'date': DateTime('2010/01/03')},
             {'path': '/plone/folder',
              'action': 'changed',
              'date': DateTime('2010/01/04')}],

            get_soup_activities(('path', 'action', 'date')))
