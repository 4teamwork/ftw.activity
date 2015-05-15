from collective.lastmodifier.interfaces import ILastModifier
from ftw.activity.catalog.record import ActivityRecord
from souper.soup import get_soup
from zope.component import queryAdapter
from zope.component.hooks import getSite


def get_activity_soup():
    return get_soup('activity', getSite())


def object_added(context, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'added', actor_userid=actor_userid, date=date)
    return soup.add(record)


def object_changed(context, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'changed', actor_userid=actor_userid, date=date)
    return soup.add(record)


def object_deleted(context, actor_userid=None, date=None):
    soup = get_activity_soup()
    record = ActivityRecord(context, 'deleted', actor_userid=actor_userid, date=date)
    return soup.add(record)


def index_object(obj):
    """Indexes an object when it was never indexed.
    This creates a "created" activity.
    If the object was modified after creating, it also creates a "changed" activity.
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
