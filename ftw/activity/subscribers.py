from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.activity.catalog import comment_added
from ftw.activity.catalog import comment_removed
from ftw.activity.catalog import object_added
from ftw.activity.catalog import object_changed
from ftw.activity.catalog import object_deleted
from ftw.activity.catalog import object_moved
from ftw.activity.catalog import object_transition
from ftw.activity.utils import IS_PLONE_5
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component.hooks import getSite


def is_supported(context):
    # IUUID support is required for all records in order
    # to be able to store the uuid of the object.
    return IUUID(context, None) is not None


def make_object_added_activity(context, event):
    is_cloned = event.__class__.__name__ == 'ObjectClonedEvent'

    if IS_PLONE_5 and is_cloned:
        return None

    if not is_supported(context) or IPloneSiteRoot.providedBy(event.object):
        return None

    object_added(context)


def make_object_changed_activity(context, event):
    in_aqcuisition = aq_parent(aq_inner(context))
    # Move/rename triggers a container modified change event.
    is_container_modified = event.__class__.__name__ == 'ContainerModifiedEvent'
    if not in_aqcuisition or is_container_modified or not is_supported(context):
        return

    object_changed(context)


def make_object_deleted_activity(context, event):
    # When deleting the Plone Site, getSite() is None
    # and we can abort recording activities.
    if getSite() is None or not is_supported(context):
        return None
    object_deleted(context)


def make_object_transition_activity(context, event):
    if not event.transition or not is_supported(context):
        return None

    object_transition(context,
                      transition=event.transition.getId(),
                      workflow=event.workflow.getId(),
                      old_state=event.old_state.getId(),
                      new_state=event.new_state.getId())


def make_object_moved_activity(context, event):
    if not event.oldParent or not event.newParent or not is_supported(context):
        return None

    if event.oldParent == event.newParent:
        # The object was not moved, but renamed.
        return

    object_moved(context,
                 old_parent=event.oldParent,
                 new_parent=event.newParent)


def make_comment_added_activity(context, event):
    if not is_supported(context):
        return None

    comment_added(context, event.comment)


def make_comment_removed_activity(context, event):
    if not is_supported(context):
        return None

    comment_removed(context, event.comment)
