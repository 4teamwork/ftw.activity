from datetime import timedelta
from ftw.activity.interfaces import IActivityFilter
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class FilterCloseChanges(object):
    """This filter removes "changed"-activities when they occur
    in short time on the same object.
    """

    implements(IActivityFilter)
    adapts(Interface, Interface, Interface)

    time_threshold = timedelta(minutes=1)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def position(self):
        return 100

    def process(self, activities):
        previous = None
        for activity in activities:
            if self.show_activity(activity, previous):
                yield activity
            previous = activity

    def show_activity(self, this, newer):
        if not newer:
            return True

        if this.attrs['action'] != 'changed' \
           or newer.attrs['action'] != 'changed':
            return True

        if this.attrs['uuid'] != newer.attrs['uuid']:
            return True

        if this.attrs['actor'] != newer.attrs['actor']:
            return True

        this_date = this.attrs['date'].asdatetime()
        newer_date = newer.attrs['date'].asdatetime()
        return this_date < newer_date - self.time_threshold
