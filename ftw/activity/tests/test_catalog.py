from datetime import datetime
from DateTime import DateTime
from ftw.activity.catalog import comment_added
from ftw.activity.catalog import comment_removed
from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog import object_added
from ftw.activity.catalog import object_changed
from ftw.activity.catalog import object_deleted
from ftw.activity.catalog import query_soup
from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.tests.helpers import get_soup_activities
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from ftw.testing import staticuid
from plone.app.discussion.interfaces import IConversation
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from repoze.catalog.query import Eq
from unittest2 import TestCase
from zope.component import createObject


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
                           'allowed_roles_and_users': ['Anonymous'],
                           'uuid': 'testaddactivity00000000000000001',
                           'portal_type': 'Document',
                           'title': 'The Document',
                           'timestamp': 1293280200000L,
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
                           'allowed_roles_and_users': ['Anonymous'],
                           'uuid': 'testchangedactivity0000000000001',
                           'portal_type': 'Document',
                           'title': 'The Document',
                           'timestamp': 1293280200000L,
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
                           'allowed_roles_and_users': ['Anonymous'],
                           'uuid': 'testdeletedactivity0000000000001',
                           'portal_type': 'Document',
                           'title': 'The Document',
                           'timestamp': 1293280200000L,
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
                      query_soup(Eq('action', 'changed'),
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
                      query_soup(Eq('path', '/'.join(folder.getPhysicalPath()))))

        self.assertItemsEqual(['/plone/folder', '/plone/folder/one'],
                              results)

    def test_view_permission_is_required(self):
        self.layer['portal'].manage_permission('View', ['Reader', 'Manager'])
        folder = create(Builder('folder'))
        create(Builder('page').titled('Not visible').within(folder))

        user = create(Builder('user')
                      .with_roles('Reader', 'Contributor', on=folder))
        create(Builder('page').titled('Visible').within(folder))

        login(self.layer['portal'], user.getId())

        self.assertEquals(
            [{'path': '/plone/folder/visible'}],
            get_soup_activities(('path',)))

    @staticuid()
    def test_comment_added_activity(self):
        document = create(Builder('document').titled('The Document'))
        conversation = IConversation(document)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment_id = conversation.addComment(comment)

        with freeze(datetime(2010, 12, 25, 13, 30)):
            record_id = comment_added(document, comment)
        record = get_activity_soup().get(record_id)

        self.assertEquals({'path': '/plone/the-document',
                           'allowed_roles_and_users': ['Anonymous'],
                           'uuid': 'testcommentaddedactivity00000001',
                           'portal_type': 'Document',
                           'title': 'The Document',
                           'timestamp': 1293280200000L,
                           'action': 'comment:added',
                           'date': DateTime('2010/12/25 13:30:00'),
                           'actor': TEST_USER_ID,
                           'comment_id': comment_id,
                           'comment_text': 'Comment text',
                           'comment_text_mime_type': 'text/plain'},
                          dict(record.attrs))

    @staticuid()
    def test_comment_removed_activity(self):
        document = create(Builder('document').titled('The Document'))
        conversation = IConversation(document)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment_id = conversation.addComment(comment)

        with freeze(datetime(2010, 12, 25, 13, 30)):
            record_id = comment_removed(document, comment)
        record = get_activity_soup().get(record_id)

        self.assertEquals({'path': '/plone/the-document',
                           'allowed_roles_and_users': ['Anonymous'],
                           'uuid': 'testcommentremovedactivity000001',
                           'portal_type': 'Document',
                           'title': 'The Document',
                           'timestamp': 1293280200000L,
                           'action': 'comment:removed',
                           'date': DateTime('2010/12/25 13:30:00'),
                           'actor': TEST_USER_ID,
                           'comment_id': comment_id,
                           'comment_text': 'Comment text',
                           'comment_text_mime_type': 'text/plain'},
                          dict(record.attrs))
