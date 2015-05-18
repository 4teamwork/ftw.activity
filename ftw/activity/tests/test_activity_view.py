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
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
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
        with freeze(datetime(2010, 12, 26, 10, 35)) as clock:
            folder = create(Builder('folder').titled('The Folder'))

            clock.forward(days=1)
            folder.reindexObject()  # updates modified date

            clock.forward(days=1)
            file_ = create(Builder('file').titled('The First File'))

            clock.forward(hours=1)
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
        with freeze(datetime(2010, 1, 2, 1)) as clock:
            pages = [create(Builder('page').titled('Zero'))]
            clock.backward(hours=1)
            pages.append(create(Builder('page').titled('One')))
            clock.backward(hours=1)
            pages.append(create(Builder('page').titled('Two')))
            clock.backward(hours=1)
            pages.append(create(Builder('page').titled('Three')))

        start_after = pages[1].UID()
        browser.login().open(view='activity?last_uid={}'.format(start_after))
        self.assertEquals(['Two', 'Three'],
                          map(attrgetter('title'), activity.events()))

    def test_events_are_batched(self):
        pages = []
        with freeze(datetime(2010, 1, 2)) as clock:
            for index in range(6):
                clock.backward(hours=1)
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
