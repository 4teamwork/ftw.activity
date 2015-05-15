from ftw.activity.catalog import object_added
from ftw.activity.catalog import object_changed
from ftw.activity.catalog import object_deleted


def make_object_added_activity(context, event):
    object_added(context)


def make_object_changed_activity(context, event):
    object_changed(context)


def make_object_deleted_activity(context, event):
    object_deleted(context)
