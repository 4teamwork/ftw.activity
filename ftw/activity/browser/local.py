from ftw.activity.browser.activity import ActivityView
from ftw.activity.interfaces import IActivityFilter
from ftw.activity.interfaces import ILocalActivityView
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class LocalActivityView(ActivityView):
    implements(ILocalActivityView)


class LocalActivityFilter(object):
    """This filters all activities of contents which are not the
    current context but within the current context.

    This means we are breaking the default recursivity of the souper
    catalog.

    The problem is that a Eq('path', path) query is recursive and
    the index is not able to do a non-recursive query with the path
    index.
    """

    implements(IActivityFilter)
    adapts(Interface, Interface, ILocalActivityView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def position(self):
        return 50

    def process(self, activities):
        path = '/'.join(self.context.getPhysicalPath())
        for activity in activities:
            if activity.attrs['path'] != path:
                continue
            yield activity
