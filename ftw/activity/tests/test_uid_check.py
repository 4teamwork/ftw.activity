from ftw.activity.subscribers import is_supported
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest import TestCase


class TestUIDCheck(TestCase):
    """ is_supported checks if the object of the event can be used
        to create an activity event.
        This prevents errors in Plone when moving objects whose actions
        cannot be indexed by ftw.activity.
    """

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        self.portal = self.layer['portal']

    def test_plone_site_is_not_supported(self):
        self.assertFalse(is_supported(self.portal))

    def test_scripts_are_not_supported(self):
        # Example script from Plone
        self.assertFalse(is_supported(self.portal.checkUpToDate))

    # Test some default content types just in case
    def test_file_is_supported(self):
        self.assertTrue(is_supported(create(Builder('file'))))

    def test_folder_is_supported(self):
        self.assertTrue(is_supported(create(Builder('folder'))))
