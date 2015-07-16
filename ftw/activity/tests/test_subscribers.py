from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.helpers import get_soup_activities
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import staticuid
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.utils import getToolByName
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

    def test_activity_for_workflow_transition_is_added(self):
        wftool = getToolByName(self.layer['portal'], 'portal_workflow')
        wftool.setChainForPortalTypes(['Document'], 'simple_publication_workflow')

        doc = create(Builder('document').titled(u'The Document'))
        wftool.doActionFor(doc, 'publish')

        self.assertEquals(
            [{'path': '/plone/the-document',
              'action': 'added'},

             {'path': '/plone/the-document',
              'action': 'transition',
              'transition': 'publish',
              'workflow': 'simple_publication_workflow',
              'old_state': 'private',
              'new_state': 'published'}],

            get_soup_activities(('path', 'action', 'transition', 'workflow',
                                 'old_state', 'new_state')))

    def test_activity_for_object_copied_is_added(self):
        folder = create(Builder('folder'))
        doc = create(Builder('document').within(folder))

        clipboard = folder.manage_copyObjects(doc.getId())
        folder.manage_pasteObjects(clipboard)

        self.assertEquals(
            [{'path': '/plone/folder',
              'action': 'added'},
             {'path': '/plone/folder/document',
              'action': 'added'},
             {'path': '/plone/folder/copy_of_document',
              'action': 'added'}],

            get_soup_activities(('path', 'action')))

    @staticuid()
    def test_moving_objects(self):
        source = create(Builder('folder').titled('Source'))
        target = create(Builder('folder').titled('Target'))
        doc = create(Builder('document').within(source))

        clipboard = source.manage_cutObjects(doc.getId())
        target.manage_pasteObjects(clipboard)

        self.assertEquals(
            [{'action': 'added', 'path': '/plone/source'},
             {'action': 'added', 'path': '/plone/target'},
             {'action': 'added', 'path': '/plone/source/document'},
             {'action': 'moved', 'path': '/plone/target/document',
              'old_parent_path': '/plone/source',
              'old_parent_uuid': 'testmovingobjects000000000000001',
              'new_parent_path': '/plone/target',
              'new_parent_uuid': 'testmovingobjects000000000000002'}],

            get_soup_activities(('path',
                                 'action',
                                 'old_parent_path',
                                 'old_parent_uuid',
                                 'new_parent_path',
                                 'new_parent_uuid')))

    def test_renaming_object_creates_no_record(self):
        # Renaming means changing the ID / URL of a content,
        # but not changing it's title.
        # Since this is normally not important for the common user,
        # we don't create records in this case.
        # There is no profound reason though.

        folder = create(Builder('folder'))
        create(Builder('document').titled(u'Foo').within(folder))
        folder.manage_renameObject('foo', 'bar')

        self.assertEquals(
            [{'path': '/plone/folder',
              'action': 'added'},
             {'path': '/plone/folder/foo',
              'action': 'added'}],

            get_soup_activities(('path', 'action')))
