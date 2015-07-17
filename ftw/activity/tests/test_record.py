from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from datetime import datetime
from ftw.activity.catalog.record import ActivityRecord
from ftw.activity.interfaces import IActivityCreatedEvent
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getSiteManager


class TestCatalog(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_record_created_event_is_fired(self):
        doc = create(Builder('document'))

        events = []
        getSiteManager().registerHandler(events.append, [IActivityCreatedEvent])

        record = ActivityRecord(doc, 'added')
        self.assertEquals(1, len(events), 'Expected exactly one event.')
        event, = events
        self.assertEquals(doc, event.object)
        self.assertEquals(record, event.activity)

    def test_record_string_representation(self):
        record = ActivityRecord(create(Builder('document')), 'added')
        self.assertEquals('<ActivityRecord "added" for "/plone/document">',
                          str(record))

    def test_get_object_of_record__archetypes(self):
        doc = create(Builder('document').titled('Foo'))
        record = ActivityRecord(doc, 'added')

        self.assertEquals(doc, record.get_object())

        aq_parent(aq_inner(doc)).manage_delObjects([doc.getId()])
        self.assertEquals(None, record.get_object(),
                          'get_object should return None if the object is deleted.')

        create(Builder('document').titled('Foo'))
        self.assertEquals(None, record.get_object(),
                          'get_object should return None when the object at the path'
                          ' is not the same object.')

    def test_get_object_of_record__dexterity(self):
        doc = create(Builder('dx type').titled(u'Foo'))
        record = ActivityRecord(doc, 'added')

        self.assertEquals(doc, record.get_object())

        aq_parent(aq_inner(doc)).manage_delObjects([doc.getId()])
        self.assertEquals(None, record.get_object(),
                          'get_object should return None if the object is deleted.')

        create(Builder('dx type').titled(u'Foo'))
        self.assertEquals(None, record.get_object(),
                          'get_object should return None when the object at the path'
                          ' is not the same object.')

    @browsing
    def test_get_actor_info(self, browser):
        self.portal.invokeFactory('Folder', 'Members')
        mtool = getToolByName(self.portal, 'portal_membership')
        mtool.setMemberareaCreationFlag()

        hugo = create(Builder('user').named('Hugo', 'Boss'))
        mtool.createMemberArea(hugo.getId())
        record = ActivityRecord(create(Builder('document')),
                                'added',
                                actor_userid=hugo.getId())

        self.assertEquals(
            {'url': 'http://nohost/plone/Members/hugo.boss',
             'portrait_url': 'http://nohost/plone/defaultUser.png',
             'fullname': 'Boss Hugo'},
            record.get_actor_info())

    def test_get_actor_info_for_non_existing_user(self):
        record = ActivityRecord(create(Builder('document')),
                                'added',
                                actor_userid='john.doe')

        self.assertEquals(
            {'url': '',
             'portrait_url': 'http://nohost/plone/defaultUser.png',
             'fullname': 'john.doe'},
            record.get_actor_info())

    def test_get_pretty_date(self):
        doc = create(Builder('document').titled('Foo'))
        record = ActivityRecord(doc, 'added')

        with freeze(datetime(2010, 1, 2)) as clock:
            record = ActivityRecord(doc, 'added')

            clock.forward(days=1)
            self.assertEquals({'relative': u'yesterday',
                               'absolute': DateTime('2010/01/02')},
                              record.get_pretty_date())

    def test_translated_portal_type(self):
        record = ActivityRecord(create(Builder('document')), 'added')
        self.assertEquals('Document', record.translated_portal_type())

    def test_allowed_roles_and_users(self):
        self.portal.manage_permission('View', ['Reader', 'Manager'])
        create(Builder('user').with_roles('Reader', on=self.portal))
        record = ActivityRecord(create(Builder('document')), 'added')
        self.assertEquals(
            ['user:john.doe', 'Manager', 'Reader'],
            record.attrs['allowed_roles_and_users'])
