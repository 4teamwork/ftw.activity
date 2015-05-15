from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.helpers import get_soup_activities
from ftw.builder import Builder
from ftw.builder import create
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Archetypes.event import ObjectEditedEvent
from unittest2 import TestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestSubscribers(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

    def test_activity_for_creating_is_added(self):
        create(Builder('document'))
        create(Builder('dx type'))

        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/dxtype',
              'action': 'added'}],
            get_soup_activities())

    def test_activity_for_changing_is_added(self):
        notify(ObjectEditedEvent(create(Builder('document'))))
        notify(ObjectModifiedEvent(create(Builder('dx type'))))

        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/document',
              'action': 'changed'},
             {'path': '/plone/dxtype',
              'action': 'added'},
             {'path': '/plone/dxtype',
              'action': 'changed'}],
            get_soup_activities())

    def test_activity_for_deleting_is_added(self):
        doc = create(Builder('document'))
        aq_parent(aq_inner(doc)).manage_delObjects([doc.getId()])
        doc = create(Builder('dx type'))
        aq_parent(aq_inner(doc)).manage_delObjects([doc.getId()])

        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/document',
              'action': 'deleted'},
             {'path': '/plone/dxtype',
              'action': 'added'},
             {'path': '/plone/dxtype',
              'action': 'deleted'}],
            get_soup_activities())
