from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.pages import activity
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from operator import attrgetter
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase



class TestActivityView(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

    @browsing
    def test_local_activity_view_is_not_recursive(self, browser):
        folder = create(Builder('folder').titled('The Folder'))
        create(Builder('file').titled('The First File'))

        browser.login().open(folder, view='local-activity')
        self.assertEquals(
            ['The Folder'],
            map(attrgetter('title'), activity.events()))
