from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime
from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog import object_changed
from ftw.activity.tests import FunctionalTestCase
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
from plone.app.testing import TEST_USER_NAME
import transaction



class TestActivityView(FunctionalTestCase):

    @browsing
    def test_shows_added_and_modified_objects(self, browser):
        self.grant('Manager')
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
                'Added an hour ago by test_user_1_',
                file_event.byline)
            self.assertEquals('The First File', file_event.title)
            self.assertEquals('{0}/view'.format(file_.absolute_url()),
                              file_event.url,
                              '/view should be appended for files')

            self.assertEquals(
                'Added day before by test_user_1_',
                folder_event.byline)
            self.assertEquals('The Folder', folder_event.title)
            self.assertEquals(folder.absolute_url(), folder_event.url)

    @browsing
    def test_editable_border_is_hidden(self, browser):
        self.grant('Manager')
        browser.login().visit(view='activity')
        self.assertEquals('activity', plone.view())
        self.assertFalse(browser.css('.documentEditable'),
                         'Editable border is visible')

    @browsing
    def test_raw_action_is_public(self, browser):
        self.grant('Manager')
        create(Builder('folder'))
        browser.login().open(view='activity')
        self.assertEquals(1, len(activity.events()),
                          'Expected exactly one event')

    @browsing
    def test_fetch_more_events(self, browser):
        self.grant('Manager')
        foo = create(Builder('page').titled('Foo'))
        bar = create(Builder('page').titled('Bar'))
        get_activity_soup().clear()

        with freeze(datetime(2010, 1, 2, 1)) as clock:
            def touch(obj):
                obj.setTitle(obj.Title() + '*')
                object_changed(obj)
                clock.forward(hours=1)

            touch(foo)
            touch(bar)
            touch(foo)
            touch(bar)
            touch(foo)
            touch(bar)

        transaction.commit()

        browser.login().open(view='activity?amount_of_events=2')
        events = activity.events()
        self.assertEquals(['Bar***', 'Foo***'],
                          map(attrgetter('title'), events))

        browser.open(view='activity?amount_of_events=2&last_activity={0}'.format(
                events[-1].activity_id))
        events = activity.events()
        self.assertEquals(['Bar**', 'Foo**'],
                          map(attrgetter('title'), events))

        browser.open(view='activity?amount_of_events=2&last_activity={0}'.format(
                events[-1].activity_id))
        events = activity.events()
        self.assertEquals(['Bar*', 'Foo*'],
                          map(attrgetter('title'), events))

        browser.open(view='activity?amount_of_events=2&last_activity={0}'.format(
                events[-1].activity_id))
        events = activity.events()
        self.assertEquals([],
                          map(attrgetter('title'), events))

    def test_events_are_batched(self):
        self.grant('Manager')
        pages = []
        with freeze(datetime(2010, 1, 2)) as clock:
            for index in range(7):
                clock.backward(hours=1)
                pages.append(create(Builder('page')
                                    .titled('Page {0}'.format(index))))

        view = self.layer['portal'].restrictedTraverse('@@activity')

        activity_repr = lambda repr: {'title': repr['activity'].attrs['title'],
                                      'is_last': repr['is_last_activity']}

        events = list(view.events(amount=3))
        self.assertEquals([{'title': 'Page 0', 'is_last': False},
                           {'title': 'Page 1', 'is_last': False},
                           {'title': 'Page 2', 'is_last': False}],
                          map(activity_repr, events))

        events = list(view.events(amount=3, last_activity=events[-1]['activity_id']))
        self.assertEquals([{'title': 'Page 3', 'is_last': False},
                           {'title': 'Page 4', 'is_last': False},
                           {'title': 'Page 5', 'is_last': False}],
                          map(activity_repr, events))

        events = list(view.events(amount=3, last_activity=events[-1]['activity_id']))
        self.assertEquals([{'title': 'Page 6', 'is_last': True}],
                          map(activity_repr, events))

    @browsing
    def test_actor_not_available(self, browser):
        """
        This test makes sure that there won't be an error if the user who
        created an object is no longer available.
        """
        self.grant('Manager')
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

    @browsing
    def test_delete_events_are_shown(self, browser):
        self.grant('Manager')
        with freeze(datetime(2010, 1, 2)) as clock:
            page = create(Builder('page').titled('The Page'))

            browser.login().open(view='activity')
            self.assertEquals(
                [{'title': 'The Page',
                  'url': 'http://nohost/plone/the-page',
                  'byline': 'Added now by test_user_1_'}],
                activity.events_infos())

            clock.forward(hours=1)
            aq_parent(aq_inner(page)).manage_delObjects([page.getId()])
            transaction.commit()

            browser.reload()
            self.assertEquals(
                [{'title': 'The Page',
                  'url': None,
                  'byline': 'Deleted now by test_user_1_'},
                 {'title': 'The Page',
                  'url': None,
                  'byline': 'Added an hour ago by test_user_1_'}],
                activity.events_infos())

    @browsing
    def test_comment_is_shown(self, browser):
        """
        This test makes sure that the comment text of a comment activity
        is shown in the feed (cropped).
        """
        self.grant('Manager')
        self.enable_discussion_for_document()
        browser.login().visit(create(Builder('document').titled(u'The Page')))
        browser.fill({'Comment': '''Lorem ipsum dolor sit amet, consectetur
        adipiscing elit. Atque haec ita iustitiae propria sunt, ut sint
        virtutum reliquarum communia. Quod autem in homine praestantissimum
        atque optimum est, id deseruit. An vero displicuit ea, quae tributa
        est animi virtutibus tanta praestantia? Et quidem illud ipsum non
        nimium probo et tantum patior, philosophum loqui de cupiditatibus
        finiendis. Nulla profecto est, quin suam vim retineat a primo ad
        extremum.'''}).submit()

        browser.open(view='activity')
        self.assertEquals(
            [{'title': 'The Page',
              'url': 'http://nohost/plone/the-page',
              'byline': 'Comment added now by test_user_1_'},
             {'title': 'The Page',
              'url': 'http://nohost/plone/the-page',
              'byline': 'Added now by test_user_1_'}],
            activity.events_infos())

        self.assertEquals(
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
            ' Atque haec ita iustitiae propria ...',
            activity.events()[0].body_text)
