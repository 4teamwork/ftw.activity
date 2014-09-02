from datetime import datetime
from datetime import timedelta
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.pages import activity
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestActivityView(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Contributor'])

    @browsing
    def test_shows_created_and_modified_objects(self, browser):
        now = datetime(2010, 12, 28, 10, 35)
        with freeze(now - timedelta(days=2)):
            folder = create(Builder('folder').titled('The Folder'))

        with freeze(now - timedelta(days=1)):
            folder.reindexObject()  # updates modified date

        with freeze(now - timedelta(hours=1)):
            create(Builder('page').titled('The First Page'))

        with freeze(now):
            browser.login().open(view='activity')
            self.assertEquals(2, len(activity.events()),
                              'Expected exactly two events')

            page_event, folder_event = activity.events()
            self.assertEquals(
                'test_user_1_ has created Document an hour ago',
                page_event.byline)
            self.assertEquals('The First Page', page_event.title)

            self.assertEquals(
                'test_user_1_ has modified Folder yesterday',
                folder_event.byline)
            self.assertEquals('The Folder', folder_event.title)
