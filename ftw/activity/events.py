from ftw.activity.interfaces import IActivityCreatedEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class ActivityCreatedEvent(ObjectEvent):
    """An activity has been created.
    """

    implements(IActivityCreatedEvent)

    def __init__(self, obj, activity):
        super(ActivityCreatedEvent, self).__init__(obj)
        self.activity = activity
        self.action = activity.attrs['action']
