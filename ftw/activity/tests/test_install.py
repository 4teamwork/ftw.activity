from ftw.activity.testing import FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestInstalling(TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_setup = getToolByName(self.portal, 'portal_setup')

    def test_default_profile_installed(self):
        version = self.portal_setup.getLastVersionForProfile(
            'ftw.activity:default')
        self.assertNotEqual(version, None)
        self.assertNotEqual(version, 'unknown')
