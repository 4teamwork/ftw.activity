from ftw.activity.catalog import object_added
from ftw.activity.catalog import object_changed
from ftw.activity.catalog import object_deleted
from ftw.activity.catalog import object_moved
from ftw.activity.catalog import object_transition
from zope.component.hooks import getSite


def make_object_added_activity(context, event):
    object_added(context)


def make_object_changed_activity(context, event):
    object_changed(context)


def make_object_deleted_activity(context, event):
    # When deleting the Plone Site, getSite() is None
    # and we can abort recording activities.
    if getSite() is None:
        return None
    object_deleted(context)


def make_object_transition_activity(context, event):
    if not event.transition:
        return

    object_transition(context,
                      transition=event.transition.getId(),
                      workflow=event.workflow.getId(),
                      old_state=event.old_state.getId(),
                      new_state=event.new_state.getId())


def make_object_moved_activity(context, event):
    if not event.oldParent or not event.newParent:
        return

    if event.oldParent == event.newParent:
        # The object was not moved, but renamed.
        return

    object_moved(context,
                 old_parent=event.oldParent,
                 new_parent=event.newParent)
