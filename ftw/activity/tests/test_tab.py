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
    def test_fetch_more_events(self, browser):
        with freeze(datetime(2010, 1, 2)) as clock:
            create(Builder('page').titled('One'))
            clock.backward(days=1)
            create(Builder('page').titled('Two'))
            clock.backward(days=1)
            create(Builder('page').titled('Three'))

        browser.login().open(view='tabbedview_view-activity')
        self.assertEquals(['One', 'Two', 'Three'],
                          map(attrgetter('title'), activity.events()))
