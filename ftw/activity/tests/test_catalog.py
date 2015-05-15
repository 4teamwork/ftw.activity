from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime
from DateTime import DateTime
from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog import object_added
from ftw.activity.catalog import object_changed
from ftw.activity.catalog import object_deleted
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from ftw.testing import staticuid
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from repoze.catalog.query import Eq
from unittest2 import TestCase


class TestCatalog(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

    @staticuid()
    def test_add_activity(self):
        document = create(Builder('document').titled('The Document'))
        with freeze(datetime(2010, 12, 25, 13, 30)):
            record_id = object_added(document)
        record = get_activity_soup().get(record_id)

        self.assertEquals({'path': '/plone/the-document',
                           'uuid': 'testaddactivity00000000000000001',
                           'portal_type': 'Document',
                           'action': 'added',
                           'date': DateTime('2010/12/25 13:30:00'),
                           'actor': TEST_USER_ID},
                          dict(record.attrs))

    @staticuid()
    def test_changed_activity(self):
        document = create(Builder('document').titled('The Document'))
        with freeze(datetime(2010, 12, 25, 13, 30)):
            record_id = object_changed(document)
        record = get_activity_soup().get(record_id)

        self.assertEquals({'path': '/plone/the-document',
                           'uuid': 'testchangedactivity0000000000001',
                           'portal_type': 'Document',
                           'action': 'changed',
                           'date': DateTime('2010/12/25 13:30:00'),
                           'actor': TEST_USER_ID},
                          dict(record.attrs))

    @staticuid()
    def test_deleted_activity(self):
        document = create(Builder('document').titled('The Document'))
        with freeze(datetime(2010, 12, 25, 13, 30)):
            record_id = object_deleted(document)
        record = get_activity_soup().get(record_id)

        self.assertEquals({'path': '/plone/the-document',
                           'uuid': 'testdeletedactivity0000000000001',
                           'portal_type': 'Document',
                           'action': 'deleted',
                           'date': DateTime('2010/12/25 13:30:00'),
                           'actor': TEST_USER_ID},
                          dict(record.attrs))

    def test_querying(self):
        soup = get_activity_soup()
        document = create(Builder('document'))
        soup.clear()

        with freeze(datetime(2010, 1, 1)):
            object_added(document)
        with freeze(datetime(2010, 1, 2)):
            object_changed(document)
        with freeze(datetime(2010, 1, 3)):
            object_changed(document)

        results = map(lambda record: (record.attrs['action'], record.attrs['date']),
                      soup.query(Eq('action', 'changed'),
                                 sort_index='date',
                                 reverse=True))

        self.assertEquals([('changed', DateTime('2010/01/03')),
                           ('changed', DateTime('2010/01/02'))],
                          results)

    def test_querying_by_path(self):
        soup = get_activity_soup()
        folder = create(Builder('folder'))
        doc1 = create(Builder('document').titled('One').within(folder))
        doc2 = create(Builder('document').titled('Two'))

        soup.clear()
        map(object_added, (folder, doc1, doc2))

        results = map(lambda record: record.attrs['path'],
                      soup.query(Eq('path', '/'.join(folder.getPhysicalPath()))))

        self.assertItemsEqual(['/plone/folder', '/plone/folder/one'],
                              results)

    def test_get_object_of_record(self):
        doc = create(Builder('document').titled('Foo'))
        record = get_activity_soup().get(object_added(doc))

        self.assertEquals(doc, record.get_object())

        aq_parent(aq_inner(doc)).manage_delObjects([doc.getId()])
        self.assertEquals(None, record.get_object(),
                          'get_object should return None if the object is deleted.')

        create(Builder('document').titled('Foo'))
        self.assertEquals(None, record.get_object(),
                          'get_object should return None when the object at the path'
                          ' is not the same object.')

    def test_record_string_representation(self):
        record_id = object_added(create(Builder('document')))
        record = get_activity_soup().get(record_id)
        self.assertEquals('<ActivityRecord "added" for "/plone/document">',
                          str(record))
