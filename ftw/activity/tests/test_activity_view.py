from collective.lastmodifier.interfaces import ILastModifier
from datetime import datetime
from datetime import timedelta
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.pages import activity
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from operator import attrgetter
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
            file_ = create(Builder('file').titled('The First File'))

        with freeze(now):
            browser.login().open(view='activity')
            self.assertEquals(2, len(activity.events()),
                              'Expected exactly two events')

            file_event, folder_event = activity.events()
            self.assertEquals(
                'File created an hour ago by test_user_1_',
                file_event.byline)
            self.assertEquals('The First File', file_event.title)
            self.assertEquals('{0}/view'.format(file_.absolute_url()),
                              file_event.url,
                              '/view should be appended for files')

            self.assertEquals(
                'Folder modified yesterday by test_user_1_',
                folder_event.byline)
            self.assertEquals('The Folder', folder_event.title)
            self.assertEquals(folder.absolute_url(), folder_event.url)

    @browsing
    def test_fetch_more_events(self, browser):
        pages = [create(Builder('page').titled('Zero')),
                 create(Builder('page').titled('One')),
                 create(Builder('page').titled('Two')),
                 create(Builder('page').titled('Three'))]

        start_after = pages[1].UID()
        browser.login().open(view='activity?last_uid={}'.format(start_after))
        self.assertEquals(['Two', 'Three'],
                          map(attrgetter('title'), activity.events()))

    @browsing
    def test_events_are_filtered_and_batched(self, browser):
        now = datetime(2010, 12, 28, 10, 35)
        pages = []
        for index in range(6):
            with freeze(now - timedelta(hours=index)):
                pages.append(create(Builder('page')
                                    .titled('Page {0}'.format(index))))

        ILastModifier(pages[1]).set(None)
        view = self.layer['portal'].restrictedTraverse('@@activity')

        get_title = lambda repr: repr.context.Title()

        self.assertEquals(['Page 0', 'Page 2', 'Page 3'],
                          map(get_title, view.events(amount=3)))

        self.assertEquals(['Page 4', 'Page 5'],
                          map(get_title,
                              view.events(amount=3, last_uid=pages[3].UID())))
