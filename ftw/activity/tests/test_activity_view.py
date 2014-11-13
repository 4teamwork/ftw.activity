from datetime import datetime
from datetime import timedelta
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.pages import activity
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.testing import freeze
from operator import attrgetter
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getUtility
import transaction


class TestActivityView(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

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
    def test_editable_border_is_hidden(self, browser):
        browser.login().visit(view='activity')
        self.assertEquals('activity', plone.view())
        self.assertFalse(browser.css('.documentEditable'),
                         'Editable border is visible')

    @browsing
    def test_raw_action_is_public(self, browser):
        create(Builder('folder'))
        browser.login().open(view='activity')
        self.assertEquals(1, len(activity.events()),
                          'Expected exactly one event')

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
    def test_events_are_batched(self, browser):
        now = datetime(2010, 12, 28, 10, 35)
        pages = []
        for index in range(6):
            with freeze(now - timedelta(hours=index)):
                pages.append(create(Builder('page')
                                    .titled('Page {0}'.format(index))))

        view = self.layer['portal'].restrictedTraverse('@@activity')

        get_title = lambda repr: repr.context.Title()
        self.assertEquals(['Page 0', 'Page 1', 'Page 2'],
                          map(get_title, view.events(amount=3)))

        self.assertEquals(['Page 3', 'Page 4', 'Page 5'],
                          map(get_title,
                              view.events(amount=3, last_uid=pages[2].UID())))

    @browsing
    def test_collections_are_supported(self, browser):
        collection = create(Builder('collection')
                            .titled('The Collection')
                            .from_query({'portal_type': 'Folder'})
                            .having(sort_on='modified',
                                    sort_reversed=True))

        now = datetime(2010, 12, 28, 10, 35)
        with freeze(now - timedelta(hours=1)):
            create(Builder('page').titled('A Page'))
            create(Builder('folder').titled('First Folder'))

        with freeze(now - timedelta(hours=2)):
            create(Builder('folder').titled('Second Folder'))

        with freeze(now):
            browser.login().open(collection, view='activity')
        self.assertEquals(
            ['First Folder', 'Second Folder'],
            map(attrgetter('title'), activity.events()))

    @browsing
    def test_collections_show_editable_border_for_default_view(self, browser):
        collection = create(Builder('collection')
                            .titled('The Collection')
                            .from_query({'portal_type': 'Collection'})
                            .having(sort_on='modified',
                                    sort_reversed=True))
        collection._setProperty('layout', 'activity', 'string')
        transaction.commit()

        browser.login().open(collection)
        self.assertEquals('activity', plone.view())
        self.assertTrue(browser.css('.documentEditable'),
                        'Editable border is not visible')

    @browsing
    def test_comments_do_not_break_activity_view(self, browser):
        registry = getUtility(IRegistry)
        registry['plone.app.discussion.interfaces'
                 '.IDiscussionSettings.globally_enabled'] = True

        types = getToolByName(self.layer['portal'], 'portal_types')
        types['Document'].allow_discussion = True
        transaction.commit()

        page = create(Builder('document'))
        browser.login().visit(page)
        browser.fill({'Comment': 'Hello World'}).submit()
        browser.visit(view='activity')
        self.assertEquals(
            1, len(activity.events()),
            'Expected only page creation event to be visible.')

    @browsing
    def test_actor_not_available(self, browser):
        """
        This test makes sure that there won't be an error if the user who
        created an object is no longer available.
        """
        # Become admin and create an unprivileged user.
        login(self.layer['portal'], TEST_USER_NAME)
        user = create(Builder('user').with_roles('Contributor'))
        logout()

        # Become the unprivileged and create an object.
        login(self.layer['portal'], user.getId())
        create(Builder('folder'))
        logout()

        # Become admin again and delete the unprivileged user.
        login(self.layer['portal'], TEST_USER_NAME)
        api.user.delete(user=user)
        transaction.commit()

        # Test.
        browser.login().open(view='activity')
        self.assertEquals(1, len(activity.events()),
                          'Expected exactly one event')
