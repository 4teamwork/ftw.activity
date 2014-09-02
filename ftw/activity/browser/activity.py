from ftw.activity.interfaces import IActivityRepresentation
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ActivityView(BrowserView):

    activity_template = ViewPageTemplateFile('templates/activity.pt')
    events_template = ViewPageTemplateFile('templates/events.pt')

    def __call__(self):
        return self.activity_template()

    def fetch(self):
        """Action for retrieving more events (based on `last_uid` in
        the request) with AJAX.
        """
        return self.events_template()

    def events(self, amount=10, last_uid=None):
        last_uid = last_uid or self.request.get('last_uid', None)
        brains = self._lookup()
        if last_uid:
            brains = self._begin_after(last_uid, brains)
        representations = self._build_representations(brains)
        representations = self._filter_invisible(representations)
        representations = self._batch_to(amount, representations)
        return representations

    def query(self):
        return {'path': '/'.join(self.context.getPhysicalPath()),
                'sort_on': 'modified',
                'sort_order': 'reverse'}

    def _lookup(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(self.query())

    def _begin_after(self, last_uid, brains):
        found = False
        for brain in brains:
            if found:
                yield brain
            elif brain.UID == last_uid:
                found = True

    def _build_representations(self, brains):
        for brain in brains:
            obj = brain.getObject()
            representation = getMultiAdapter((obj, self.request),
                                             IActivityRepresentation)
            yield representation

    def _filter_invisible(self, representations):
        for repr in representations:
            if repr.visible():
                yield repr

    def _batch_to(self, amount, representations):
        for index, repr in enumerate(representations):
            if index >= amount:
                break
            yield repr
