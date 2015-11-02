from datetime import datetime
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
    def test_activity_fetch_url_points_to_activity_tab(self, browser):
        browser.login().open(view='tabbed_view/listing?view_name=activity')
        self.assertEquals(
            'http://nohost/plone/tabbedview_view-activity/fetch',
            browser.css('.events').first.attrib.get('data-fetch-url'))

    @browsing
    def test_render_events(self, browser):
        with freeze(datetime(2010, 1, 2)) as clock:
            create(Builder('page').titled('One'))
            clock.backward(days=1)
            create(Builder('page').titled('Two'))
            clock.backward(days=1)
            create(Builder('page').titled('Three'))

        browser.login().open(view='tabbedview_view-activity')
        self.assertEquals(['One', 'Two', 'Three'],
                          map(attrgetter('title'), activity.events()))

    @browsing
    def test_fetch_is_traversable(self, browser):
        create(Builder('page').titled('One'))
        browser.login().open(view='tabbedview_view-activity/fetch')
        self.assertEquals(['One'],
                          map(attrgetter('title'), activity.events()))
