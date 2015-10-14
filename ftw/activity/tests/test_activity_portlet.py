from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


def portlet():
    portlets = browser.css('.portletActivity')
    if not portlets:
        return None
    return portlets.first


class TestActivityPortlet(TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

    @browsing
    def test_link_to_full_activity(self, browser):
        create(Builder('activity portlet').having(show_more=True))
        browser.visit()

        self.assertEqual(1, len(portlet().css('.showMoreLink')))

    @browsing
    def test_do_not_show_link_to_full_activity(self, browser):
        create(Builder('activity portlet').having(show_more=False))
        browser.visit()

        self.assertEqual(0, len(portlet().css('.showMoreLink')))

    @browsing
    def test_limit_activity_stream(self, browser):
        create(Builder('page'))
        create(Builder('page'))
        create(Builder('page'))

        create(Builder('activity portlet').having(count=2))
        browser.visit()

        self.assertEqual(2, len(portlet().css('.event')))

    @browsing
    def test_show_all_activities_from_navigation_root(self, browser):
        page = create(Builder('page'))
        create(Builder('page'))

        create(Builder('activity portlet'))
        browser.visit()

        self.assertEqual(2, len(portlet().css('.event')))

        browser.visit(page)

        self.assertEqual(
            2, len(portlet().css('.event')),
            'Both activites should be visible from the page')
