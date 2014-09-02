from ftw.activity.interfaces import IActivityRepresentation
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class ActivityView(BrowserView):

    def events(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return filter(None, map(self.build_event, catalog(self.query())))

    def query(self):
        return {'path': '/'.join(self.context.getPhysicalPath()),
                'sort_on': 'modified',
                'sort_order': 'reverse'}

    def build_event(self, brain):
        obj = brain.getObject()
        representation = getMultiAdapter((obj, self.request),
                                         IActivityRepresentation)
        if not representation.visible():
            return False
        return representation
