from datetime import datetime
from ftw.activity.filters import FilterCloseChanges
from ftw.activity.interfaces import IActivityFilter
from ftw.activity.tests import FunctionalTestCase
from ftw.activity.tests.pages import activity
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from operator import attrgetter
from Products.Archetypes.event import ObjectEditedEvent
from zope.event import notify
from zope.interface.verify import verifyClass
import transaction


class TestCloseChangesFilters(FunctionalTestCase):

    def test_implements_interface_correctly(self):
        verifyClass(IActivityFilter, FilterCloseChanges)

    @browsing
    def test_removes_concurrent_changes_in_less_than_1_minute(self, browser):
        self.grant('Manager')
        with freeze(datetime(2010, 1, 1, 2, 0)) as clock:
            page = create(Builder('page'))

            for _ in range(10):
                clock.forward(seconds=45)
                notify(ObjectEditedEvent(page))

            clock.forward(hours=1)
            notify(ObjectEditedEvent(page))
            transaction.commit()

            browser.login().open(view='activity')
            self.assertEquals(
                ['Changed now by test_user_1_',
                 'Changed an hour ago by test_user_1_',
                 'Added an hour ago by test_user_1_'],
                map(attrgetter('byline'), activity.events()))
