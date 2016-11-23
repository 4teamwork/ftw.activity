from collective.lastmodifier.interfaces import ILastModifier
from ftw.activity.catalog.record import ActivityRecord
from ftw.activity.utils import get_roles_and_users
from functools import partial
from plone.uuid.interfaces import IUUID
from repoze.catalog.query import And
from repoze.catalog.query import Eq
from repoze.catalog.query import Or
from souper.soup import get_soup
from zope.component import queryAdapter
from zope.component.hooks import getSite


def query_soup(queryobject, **kwargs):
    soup = get_activity_soup()
    queryobject = And(make_allowed_roles_and_users_query(),
                      queryobject)
    return soup.query(queryobject, **kwargs)


def make_allowed_roles_and_users_query(index=u'allowed_roles_and_users'):
    return reduce(Or, map(partial(Eq, index), get_roles_and_users()))


def get_activity_soup():
    return get_soup('activity', getSite())


def object_added(context, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'added',
                            actor_userid=actor_userid, date=date)
    return soup.add(record)


def object_changed(context, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'changed',
                            actor_userid=actor_userid, date=date)
    return soup.add(record)


def object_deleted(context, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'deleted',
                            actor_userid=actor_userid, date=date)
    return soup.add(record)


def object_transition(context, actor_userid=None, date=None,
                      transition=None, workflow=None,
                      old_state=None, new_state=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'transition',
                            actor_userid=actor_userid, date=date)
    record.attrs['transition'] = transition
    record.attrs['workflow'] = workflow
    record.attrs['old_state'] = old_state
    record.attrs['new_state'] = new_state
    return soup.add(record)


def object_moved(context, actor_userid=None, date=None,
                 old_parent=None, new_parent=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'moved',
                            actor_userid=actor_userid, date=date)

    if old_parent:
        record.attrs['old_parent_path'] = '/'.join(
            old_parent.getPhysicalPath())
        record.attrs['old_parent_uuid'] = IUUID(old_parent, None)

    if new_parent:
        record.attrs['new_parent_path'] = '/'.join(
            new_parent.getPhysicalPath())
        record.attrs['new_parent_uuid'] = IUUID(new_parent, None)

    return soup.add(record)


def index_object(obj):
    """Indexes an object when it was never indexed.
    This creates a "created" activity.
    If the object was modified after creating, it also creates a
    "changed" activity.
    """
    object_added(obj, actor_userid=obj.Creator(), date=obj.created())

    # modified and created are not exactly equal,
    # so we only compare down to the second:
    modified = obj.modified().asdatetime().timetuple()
    created = obj.created().asdatetime().timetuple()
    if modified == created:
        return

    last_modifier_adapter = queryAdapter(obj, ILastModifier)
    if last_modifier_adapter is not None:
        modifier = last_modifier_adapter.get()
    else:
        modifier = obj.Creator()
    object_changed(obj, actor_userid=modifier, date=obj.modified())


def comment_added(context, comment, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'comment:added',
                            actor_userid=actor_userid, date=date)
    record.attrs['comment_id'] = comment.comment_id
    record.attrs['comment_text'] = comment.text
    record.attrs['comment_text_mime_type'] = comment.mime_type
    if comment.in_reply_to:
        record.attrs['comment_in_reply_to'] = comment.in_reply_to
    return soup.add(record)


def comment_removed(context, comment, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'comment:removed',
                            actor_userid=actor_userid, date=date)
    record.attrs['comment_id'] = comment.comment_id
    record.attrs['comment_text'] = comment.text
    record.attrs['comment_text_mime_type'] = comment.mime_type
    if comment.in_reply_to:
        record.attrs['comment_in_reply_to'] = comment.in_reply_to
    return soup.add(record)
