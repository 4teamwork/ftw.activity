from ftw.activity.catalog.record import ActivityRecord
from souper.soup import get_soup
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
