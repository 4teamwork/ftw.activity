from ftw.activity.catalog import get_activity_soup
from ftw.activity.interfaces import IActivityRenderer
from operator import itemgetter
from plone.memoize import instance
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from repoze.catalog.query import Eq
from zope.component import getAdapters


class ActivityView(BrowserView):

    activity_template = ViewPageTemplateFile('templates/activity.pt')
    raw_template = ViewPageTemplateFile('templates/activity_raw.pt')
    events_template = ViewPageTemplateFile('templates/events.pt')

    def __call__(self):
        return self.activity_template()

    def fetch(self):
        """Action for retrieving more events (based on `last_uid` in
        the request) with AJAX.
        """
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        # The HTML stripped in order to have empty response content when
        # there are no tags at all, so that diazo does not try to
        # parse it.
        return self.events_template().strip()

    def raw(self):
        """Action for embedding activity stream into another view.
        The returned HTML does not contain a complete page with
        head / body but only the stream fragment.
        """
        return self.raw_template()

    def events(self, amount=None, last_uid=None):
        amount = amount or self.request.get('amount_of_events', 10)
        last_uid = last_uid or self.request.get('last_uid', None)
        activities = self._lookup()
        if last_uid:
            activities = self._begin_after(last_uid, activities)
        activities = self._batch_to(amount, activities)
        return self._lookup_renderers_for_activities(activities)

    def query(self):
        return Eq('path', '/'.join(self.context.getPhysicalPath()))

    def _lookup(self):
        soup = get_activity_soup()
        return soup.query(self.query(), sort_index='date', reverse=True)

    def _begin_after(self, last_uid, activities):
        found = False
        for activity in activities:
            if found:
                yield activity
            elif activity.attrs['uuid'] == last_uid:
                found = True

    def _batch_to(self, amount, activities):
        for index, repr in enumerate(activities):
            if index >= amount:
                break
            yield repr

    def _lookup_renderers_for_activities(self, activities):
        for activity in activities:
            obj = activity.get_object()
            yield {'uid': activity.attrs['uuid'],
                   'activity': activity,
                   'obj': obj,
                   'render': self._find_renderer_for_activity(activity, obj)}

    def _find_renderer_for_activity(self, activity, obj):
        for renderer in self._get_renderers():
            if renderer.match(activity, obj):
                return lambda: renderer.render(activity, obj)

    @instance.memoize
    def _get_renderers(self):
        adapters = getAdapters((self.context, self.request, self),
                               IActivityRenderer)
        renderers = map(itemgetter(1), adapters)
        renderers.sort(key=lambda renderer: renderer.position())
        return renderers
