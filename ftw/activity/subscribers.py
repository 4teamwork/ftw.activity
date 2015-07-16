from ftw.activity.catalog import object_added
from ftw.activity.catalog import object_changed
from ftw.activity.catalog import object_deleted
from zope.component.hooks import getSite


def make_object_added_activity(context, event):
    object_added(context)


def make_object_changed_activity(context, event):
    object_changed(context)


def make_object_deleted_activity(context, event):
    # When deleting the Plone Site, getSite() is None
    # and we can abort recording activities.
    if getSite() == None:
        return None
    object_deleted(context)
