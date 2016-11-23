from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.activity.tests import FunctionalTestCase
from ftw.activity.tests.helpers import get_soup_activities
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import staticuid
from plone.app.discussion.interfaces import IConversation
from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import transaction


class TestSubscribers(FunctionalTestCase):

    def test_activity_for_creating_is_added(self):
        self.grant('Manager')
        create(Builder('document'))
        create(Builder('dx type'))

        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/dxtype',
              'action': 'added'}],
            get_soup_activities())

    def test_activity_for_changing_is_added(self):
        self.grant('Manager')
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
        self.grant('Manager')
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
        self.grant('Manager')
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
        self.grant('Manager')
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
        self.grant('Manager')
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

    @staticuid()
    def test_moving_objects_from_plone_site(self):
        """
        This test makes sure that objects stored just below the Plone Site
        can be moved away from the Plone Site.
        """
        self.grant('Manager')
        type_to_modified = self.layer['portal'].portal_types.get('Plone Site')
        type_to_modified.allowed_content_types = ('Document',)

        source = create(Builder('document').titled('Source'))
        target = create(Builder('folder').titled('Target'))

        clipboard = source.manage_cutObjects(source.getId())
        target.manage_pasteObjects(clipboard)

        self.assertEquals(
            [{'action': 'added', 'path': '/plone/source'},
             {'action': 'added', 'path': '/plone/target'},
             {'action': 'moved', 'path': '/plone/target/source',
              'old_parent_path': '/plone',
              'old_parent_uuid': None,
              'new_parent_path': '/plone/target',
              'new_parent_uuid': 'testmovingobjectsfromplone000002'}],

            get_soup_activities(('path',
                                 'action',
                                 'old_parent_path',
                                 'old_parent_uuid',
                                 'new_parent_path',
                                 'new_parent_uuid')))

    @staticuid()
    def test_moving_objects_to_plone_site(self):
        """
        This test makes sure that objects can be move to the Plone Site.
        """
        self.grant('Manager')
        type_to_modified = self.layer['portal'].portal_types.get('Plone Site')
        type_to_modified.allowed_content_types = ('Document',)

        source = create(Builder('folder').titled('Source'))
        doc = create(Builder('document').within(source))
        target = create(Builder('folder').titled('Target'))

        clipboard = source.manage_cutObjects(doc.getId())
        target.manage_pasteObjects(clipboard)

        self.assertEquals(
            [{'action': 'added', 'path': '/plone/source'},
             {'action': 'added', 'path': '/plone/source/document'},
             {'action': 'added', 'path': '/plone/target'},
             {'action': 'moved', 'path': '/plone/target/document',
              'old_parent_path': '/plone/source',
              'old_parent_uuid': 'testmovingobjectstoplonesi000001',
              'new_parent_path': '/plone/target',
              'new_parent_uuid': 'testmovingobjectstoplonesi000003'}],

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

        self.grant('Manager')
        folder = create(Builder('folder'))
        create(Builder('document').titled(u'Foo').within(folder))
        folder.manage_renameObject('foo', 'bar')

        self.assertEquals(
            [{'path': '/plone/folder',
              'action': 'added'},
             {'path': '/plone/folder/foo',
              'action': 'added'}],

            get_soup_activities(('path', 'action')))

    @browsing
    def test_adding_a_comment(self, browser):
        """
        This test makes sure that an activity is added when a comment is created.
        """
        self.grant('Manager')
        self.enable_discussion_for_document()
        browser.login().visit(create(Builder('document')))
        browser.fill({'Comment': 'Hello World'}).submit()
        transaction.begin()

        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/document',
              'action': 'comment:added',
              'comment_text': 'Hello World'}],
            get_soup_activities(('path', 'action', 'comment_text')))

    @browsing
    def test_removing_a_comment(self, browser):
        """
        This test makes sure that an activity is added when a comment is removed.
        """
        self.grant('Manager')
        self.enable_discussion_for_document()
        browser.login().visit(create(Builder('document')))
        browser.fill({'Comment': 'Hello World'}).submit()
        browser.css('.commentBody form[name=delete]').first.submit()

        transaction.begin()
        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/document',
              'action': 'comment:added',
              'comment_text': 'Hello World'},
             {'path': '/plone/document',
              'action': 'comment:removed',
              'comment_text': 'Hello World'}],
            get_soup_activities(('path', 'action', 'comment_text')))

    @browsing
    def test_adding_and_removing_a_comment_reply(self, browser):
        """
        This test makes sure that an activity is added when a comment reply
        is created / removed.
        This requires JavaScript, therfore we cannot test it with our testbrowser.
        """
        self.grant('Manager')
        self.enable_discussion_for_document()
        conversation = IConversation(create(Builder('document')))

        comment = createObject('plone.Comment')
        comment.text = 'Comment'
        comment_id = conversation.addComment(comment)

        reply = createObject('plone.Comment')
        reply.text = 'Reply'
        reply.in_reply_to = comment_id
        reply_id = conversation.addComment(reply)

        del conversation[reply_id]

        self.maxDiff = None
        self.assertEquals(
            [{'path': '/plone/document',
              'action': 'added'},
             {'path': '/plone/document',
              'action': 'comment:added',
              'comment_text': 'Comment',
              'comment_id': comment_id},
             {'path': '/plone/document',
              'action': 'comment:added',
              'comment_text': 'Reply',
              'comment_id': reply_id,
              'comment_in_reply_to': comment_id},
             {'path': '/plone/document',
              'action': 'comment:removed',
              'comment_text': 'Reply',
              'comment_id': reply_id,
              'comment_in_reply_to': comment_id}],
            get_soup_activities(('path',
                                 'action',
                                 'comment_text',
                                 'comment_id',
                                 'comment_in_reply_to')))
